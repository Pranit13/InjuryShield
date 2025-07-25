import cv2
import logging
import time
import datetime
import os # For file path operations
from flask import Blueprint, render_template, Response, current_app, request, jsonify, url_for
import numpy as np
from typing import Union, Tuple, List, Dict, Any, Optional

from app.__init__ import global_detector 
from app.detection.video_stream import VideoStream
from app.config import app_config
from app.database.db_manager import db_manager 
from app.alerts.sms_notifier import sms_notifier 
from app.alerts.alert_logic import alert_manager
from app.analytics.data_processor import data_processor # Import DataProcessor
from app.analytics.heatmap_generator import heatmap_generator # Import HeatmapGenerator

logger = logging.getLogger(__name__)

web_routes = Blueprint('web_routes', __name__)

_current_video_stream: Optional[VideoStream] = None
_stream_source: Union[str, int, None] = None
_consecutive_violation_frames: int = 0 # Counter for consecutive violation frames

def get_video_stream(source: Union[str, int] = 0) -> Optional[VideoStream]:
    """
    Manages a single global VideoStream instance for the video_feed route.
    """
    global _current_video_stream, _stream_source
    if _current_video_stream is None or _stream_source != source:
        if _current_video_stream:
            _current_video_stream.release()
        _current_video_stream = VideoStream(source)
        if not _current_video_stream.open():
            logger.error(f"Failed to open video source {source}.")
            _current_video_stream = None
            _stream_source = None
            return None
        _stream_source = source
        logger.info(f"New video stream opened for source: {source}")
    return _current_video_stream


@web_routes.route('/')
def index():
    """
    Renders the main dashboard page with the real-time video feed.
    """
    logger.info("Accessing the main dashboard page.")
    return render_template('index.html', 
                           display_width=app_config.DISPLAY_WIDTH, 
                           display_height=app_config.DISPLAY_HEIGHT)

@web_routes.route('/history')
def history():
    """
    Renders the history page, displaying compliance logs and violation events.
    Also triggers heatmap generation for display.
    """
    logger.info("Accessing the history page and preparing reports.")
    compliance_logs = db_manager.get_all_compliance_logs(limit=200)
    violation_events = db_manager.get_all_violation_events(limit=200)
    
    # --- Generate Heatmap ---
    heatmap_filename = "violation_heatmap.png"
    heatmap_filepath = os.path.join(app_config.HEATMAP_OUTPUT_DIR, heatmap_filename)
    
    # Get violation coordinates from DB
    violation_coords = db_manager.get_violation_coordinates(max_points=app_config.HEATMAP_MAX_DATA_POINTS)
    
    # Generate heatmap image. Use a placeholder frame dimension if actual dimensions aren't available
    # (e.g., if no stream has been active yet). This assumes heatmap coordinates are relative to 1280x720.
    # For robustness, you might store frame dimensions with violations in DB.
    base_frame_dims = (app_config.DISPLAY_WIDTH, app_config.DISPLAY_HEIGHT) 
    
    generated_heatmap_path = heatmap_generator.generate_heatmap(
        violation_coords, heatmap_filepath, frame_dims=base_frame_dims
    )
    
    heatmap_url = None
    if generated_heatmap_path and os.path.exists(generated_heatmap_path):
        # Construct URL relative to 'static' folder. HEATMAP_OUTPUT_DIR is inside 'static'.
        # Assuming static folder is at project_root/static, and HEATMAP_OUTPUT_DIR is project_root/static/reports
        heatmap_url = url_for('static', filename=f'reports/{heatmap_filename}')
        logger.info(f"Heatmap generated and available at URL: {heatmap_url}")
    else:
        logger.error("Failed to generate heatmap or heatmap file not found.")

    # --- Other Analytics ---
    hourly_trends = data_processor.get_hourly_violation_trends()
    daily_summary = data_processor.get_daily_compliance_summary()
    violation_type_dist = data_processor.get_violation_type_distribution()

    return render_template('history.html', 
                           compliance_logs=compliance_logs,
                           violation_events=violation_events,
                           heatmap_url=heatmap_url,
                           hourly_trends=hourly_trends,
                           daily_summary=daily_summary,
                           violation_type_dist=violation_type_dist)

# --- API Endpoint for Real-time Metrics (for JavaScript on index.html) ---
@web_routes.route('/api/realtime_metrics')
def realtime_metrics():
    """
    API endpoint to provide real-time compliance metrics to the dashboard via AJAX.
    """
    logger.debug("Real-time metrics API requested.")
    metrics = db_manager.get_compliance_metrics_last_24_hours()
    return jsonify(metrics)

# --- Snapshot Saving Helper ---
def save_frame_snapshot(frame: np.ndarray, log_id: Optional[int] = None) -> Optional[str]:
    """
    Saves a snapshot of the given frame to disk.

    Args:
        frame (np.ndarray): The OpenCV frame (BGR).
        log_id (Optional[int]): The ID of the compliance log associated with this snapshot.
                                 Used for filename to ensure uniqueness.

    Returns:
        Optional[str]: The relative path to the saved snapshot within the 'static' folder, or None on failure.
    """
    if not app_config.SAVE_VIOLATION_SNAPSHOT:
        logger.debug("Snapshot saving is disabled by configuration.")
        return None

    if frame is None or frame.size == 0:
        logger.warning("Attempted to save an empty or invalid frame snapshot.")
        return None

    timestamp_str = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3] # microsec precision
    filename = f"violation_snapshot_{timestamp_str}"
    if log_id is not None:
        filename += f"_log{log_id}"
    filename += ".jpg"

    snapshot_full_path = os.path.join(app_config.SNAPSHOTS_DIR, filename)
    
    try:
        cv2.imwrite(snapshot_full_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90]) # Save with JPEG quality
        logger.info(f"Saved snapshot to: {snapshot_full_path}")
        # Return path relative to static folder
        return os.path.join('snapshots', filename).replace(os.sep, '/') # Use forward slashes for URLs
    except Exception as e:
        logger.error(f"Failed to save snapshot {snapshot_full_path}: {e}", exc_info=True)
        return None

def analyze_frame_for_ppe_status(detections: List[Dict[str, Any]]) -> Tuple[int, int, int, str, List[Dict[str, Any]]]:
    """
    Analyzes detected objects to determine overall PPE compliance status for a frame
    with more advanced logic to infer violations.
    """
    person_count = 0
    ppe_worn_count = 0
    violations_count = 0
    violation_details = []
    
    # Store detected class names for quick lookup and basic inference
    detected_class_names = {det['class_name'] for det in detections}
    
    # Detailed violation logic
    persons_with_violations = set() # Track unique persons with violations
    
    # Step 1: Count persons and explicit PPE detections
    for det in detections:
        class_name = det['class_name']
        if class_name == 'person':
            person_count += 1
        elif class_name in ['helmet', 'vest', 'gloves']:
            ppe_worn_count += 1

    # Step 2: Identify violations (complex logic - this is a simplification for Batch 5)
    # This logic still assumes your model outputs 'no-helmet', 'no-vest' etc.
    # For true person-specific PPE compliance, you'd need a multi-object tracker
    # to associate PPE with specific persons and check for missing items.
    
    # For now, if 'person' is detected, and a 'no-ppe' item is *also* detected generally,
    # or if an essential PPE type is not detected at all, count it as a violation.
    # This is a site-wide violation check rather than person-specific.
    
    # Essential PPE types your system aims to monitor
    essential_ppe = ['helmet', 'vest', 'gloves']
    
    # Check for explicit "no-" detections (e.g., no-helmet, no-vest)
    for det in detections:
        class_name = det['class_name']
        if class_name.startswith('no-'):
            violations_count += 1
            violation_details.append({
                'violation_type': class_name,
                'location_box': det['box'],
                'confidence': det['confidence'],
                'severity': 3 if 'helmet' in class_name else 2 # Helmets often higher severity
            })
            # If a 'no-X' is detected, it implies a person is likely missing it.
            # For this simplified model, we don't track *which* person, just that a violation exists.
            
    # Check for implicit "missing" PPE if persons are present and explicit 'no-X' is not caught
    # This is where context-aware rules could come in.
    # Example: If a "person" is detected but no "helmet" is detected anywhere in the frame
    # AND no "no-helmet" is detected. This is a very broad rule and prone to false positives.
    # A robust solution needs person-level association.
    
    if person_count > 0:
        for ppe_type in essential_ppe:
            if ppe_type not in detected_class_names and f"no-{ppe_type}" not in detected_class_names:
                # If a person is present, but an essential PPE item (and its 'no-' counterpart) is missing
                # This could be considered a potential violation, depending on context.
                # For Batch 5, we prioritize explicit 'no-' detections and then a general check.
                # This part is highly dependent on your model's outputs.
                pass # Skipping for now to rely mostly on explicit 'no-X' detections.
    
    status_message = "Compliant"
    if violations_count > 0:
        status_message = f"{violations_count} Violation(s) Detected"
    elif person_count > 0 and violations_count == 0:
        status_message = "Compliant (Persons detected, no violations)"
    elif person_count == 0:
        status_message = "No persons detected"

    logger.debug(f"Frame Analysis: Persons={person_count}, PPE Worn={ppe_worn_count}, Violations={violations_count}, Status='{status_message}'")
    return person_count, ppe_worn_count, violations_count, status_message, violation_details


def generate_frames(source: Union[str, int] = 0):
    """
    Generator function that continuously yields JPEG encoded frames from the video source.
    These frames are annotated, processed for compliance, logged, and trigger SMS alerts.
    Also handles saving violation snapshots.
    """
    global _consecutive_violation_frames # Use the global counter

    logger.info(f"Starting frame generation for source: {source}")
    
    stream = get_video_stream(source)
    if stream is None:
        logger.error(f"Cannot get video stream for source {source}. Yielding blank frames.")
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + 
               cv2.imencode('.jpg', np.zeros((480, 640, 3), dtype=np.uint8))[1].tobytes() +
               b'\r\n--frame\r\n')
        return

    if global_detector is None:
        logger.critical("PPE Detector not initialized. Cannot perform detection on stream.")
        return

    frame_interval = 1.0 / (stream.get_fps() if stream.get_fps() > 0 else 30.0)
    last_frame_time = time.time()
    last_log_time = time.time()
    
    try:
        while True:
            frame = stream.read_frame()
            if frame is None:
                logger.warning("No frame received from stream. Attempting to restart or end stream.")
                break

            current_width, current_height = frame.shape[1], frame.shape[0]
            if current_width != app_config.DISPLAY_WIDTH or current_height != app_config.DISPLAY_HEIGHT:
                frame = cv2.resize(frame, (app_config.DISPLAY_WIDTH, app_config.DISPLAY_HEIGHT), 
                                   interpolation=cv2.INTER_AREA)

            detections = global_detector.detect(frame)
            annotated_frame = global_detector.draw_detections(frame, detections)

            # --- Frame Analysis ---
            person_count, ppe_worn_count, violations_count, status_message, violation_details = \
                analyze_frame_for_ppe_status(detections)
            
            # --- Snapshot Logic ---
            if app_config.SAVE_VIOLATION_SNAPSHOT and violations_count > 0:
                _consecutive_violation_frames += 1
                if _consecutive_violation_frames >= app_config.SNAPSHOT_CONSECUTIVE_VIOLATIONS:
                    # Take snapshot if continuous violations for configured frames
                    snapshot_path = save_frame_snapshot(frame, log_id=None) # log_id will be updated later
                    if snapshot_path:
                        logger.info(f"Violation snapshot captured: {snapshot_path}")
                    _consecutive_violation_frames = 0 # Reset counter after taking snapshot
            else:
                _consecutive_violation_frames = 0 # Reset if no violation or snapshot disabled


            # --- Logging ---
            current_time = time.time()
            if (current_time - last_log_time) >= app_config.LOG_INTERVAL_SECONDS:
                logger.debug(f"Attempting to log data. Time since last log: {current_time - last_log_time:.2f}s")
                with current_app.app_context():
                    log_id = db_manager.save_compliance_log(
                        person_count=person_count,
                        ppe_worn_count=ppe_worn_count,
                        violations_count=violations_count,
                        status=status_message,
                        # Pass snapshot path if captured immediately before this log point
                        frame_snapshot_path=snapshot_path if 'snapshot_path' in locals() and snapshot_path else None
                    )
                    if log_id is not None and violations_count > 0:
                        for detail in violation_details:
                            db_manager.save_violation_event(
                                log_id=log_id,
                                violation_type=detail['violation_type'],
                                location_box=detail['location_box'],
                                confidence=detail['confidence'],
                                severity=detail['severity']
                            )
                    elif log_id is None:
                        logger.error("Failed to save compliance log, skipping violation event logging for this interval.")
                last_log_time = current_time

            # --- SMS Alerting Logic ---
            if violations_count > 0:
                for detail in violation_details:
                    violation_type = detail['violation_type']
                    if alert_manager.should_send_alert(violation_type):
                        alert_message = alert_manager.format_alert_message(
                            [detail],
                            datetime.datetime.utcnow()
                        )
                        logger.info(f"Triggering SMS alert for: {violation_type}")
                        sms_notifier.send_sms(alert_message)
                        alert_manager.record_alert_sent(violation_type)
            
            # Encode and yield frame
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                logger.error("Failed to encode frame to JPEG.")
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

            # Control frame rate
            time_to_wait = frame_interval - (current_time - last_frame_time)
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            last_frame_time = time.time()

    except Exception as e:
        logger.error(f"Error during frame generation: {e}", exc_info=True)
    finally:
        logger.info(f"Releasing video stream for source: {source}")
        pass

@web_routes.route('/video_feed')
def video_feed():
    """
    Provides the real-time video feed for the web dashboard.
    """
    logger.info("Video feed requested.")
    return Response(generate_frames(source=0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')