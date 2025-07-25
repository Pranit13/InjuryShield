import cv2
import logging
import time
import datetime
from flask import Blueprint, render_template, Response, current_app, request, jsonify
import numpy as np
from typing import Optional, List, Dict, Union, Tuple, Any
import os

from app.shared import global_detector 
from app.detection.video_stream import VideoStream
from app.config import app_config
from app.database.db_manager import db_manager # Import the DB manager
from app.extensions import db    

import torch
from app.utils.safe_loader import register_safe_classes
register_safe_classes()

from ultralytics import YOLO

model_path = "models/yolov8n.pt"  # Update path as needed
model = YOLO(model_path)
print("Model loaded successfully!")

class PPEDetector:
    def __init__(self, model_path, class_names_file, confidence_threshold=0.5, iou_threshold=0.5):
        self.model = YOLO(model_path)
        self.model.load(model_path, weights_only=False)
        self.model.to("cuda" if torch.cuda.is_available() else "cpu")
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.class_names = self._load_class_names(r"C:\Users\AI\Documents\Pranit\InjuryShield\models\classes.txt")


    def _load_class_names(self, class_names_file):
        with open(class_names_file, 'r') as f:
            return [line.strip() for line in f.readlines()]

    def detect(self, frame):
        results = self.model(frame)[0]
        detections = []
        for box, conf, cls in zip(results.boxes.xyxy, results.boxes.conf, results.boxes.cls):
            if conf < self.confidence_threshold:
                continue
            detections.append({
                'box': box.tolist(),
                'confidence': float(conf),
                'class_id': int(cls),
                'class_name': self.class_names[int(cls)]
            })
        return detections

    def draw_detections(self, frame, detections):
        for det in detections:
            x1, y1, x2, y2 = map(int, det['box'])
            label = f"{det['class_name']} {det['confidence']:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        return frame

# Get a logger for the routes module
logger = logging.getLogger(__name__)

# Create a Blueprint for web-related routes.
web_routes = Blueprint('web_routes', __name__)

# Cache for video streams to prevent re-initializing for every video_feed request.
# In a multi-user scenario, this would need more sophisticated management (e.g., per-session streams).
_current_video_stream: Optional[VideoStream] = None
_stream_source: Union[str, int, None] = None

def get_video_stream(source: Union[str, int] = 0) -> Optional[VideoStream]:
    """
    Manages a single global VideoStream instance for the video_feed route.
    This is a simplification for a single-stream demonstration.
    For production, this would be managed per-user or using a dedicated stream server.
    """
    global _current_video_stream, _stream_source
    if _current_video_stream is None or _stream_source != source:
        if _current_video_stream:
            _current_video_stream.release() # Release old stream if source changes
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
    """
    logger.info("Accessing the history page.")
    # Fetch data from the database manager
    compliance_logs = db_manager.get_all_compliance_logs(limit=200) # Fetch more for history view
    violation_events = db_manager.get_all_violation_events(limit=200)

    return render_template('history.html', 
                           compliance_logs=compliance_logs,
                           violation_events=violation_events)


def analyze_frame_for_ppe_status(detections: List[Dict[str, Any]]) -> Tuple[int, int, int, str, List[Dict[str, Any]]]:
    """
    Analyzes detected objects to determine overall PPE compliance status for a frame.
    This is where the logic for counting persons, worn PPE, and violations resides.

    Args:
        detections (List[Dict[str, Any]]): List of detected objects from the detector.

    Returns:
        Tuple[int, int, int, str, List[Dict[str, Any]]]:
            - person_count: Number of persons detected.
            - ppe_worn_count: Number of correctly worn PPE items.
            - violations_count: Number of distinct violations.
            - status_message: Overall status string (e.g., "Compliant", "Violations Detected").
            - violation_details: List of dicts for individual violation events.
    """
    person_count = 0
    ppe_worn_count = 0
    violations_count = 0
    violation_details = []
    
    # We assume that 'person' is a detected class, and 'helmet', 'no-helmet', 'vest', 'no-vest', etc.
    # are also detected. The model is expected to output these specific classes.
    
    # Simple approach for Batch 3: Count explicit 'no-ppe' detections
    # In more advanced batches, we'd associate PPE with specific persons.
    
    detected_ppe_items = {det['class_name'] for det in detections} # Set for quick lookup

    for det in detections:
        class_name = det['class_name']
        box = det['box']
        confidence = det['confidence']

        if class_name == 'person':
            person_count += 1
        
        # Count correctly worn PPE
        if class_name in ['helmet', 'vest', 'gloves']: # Add other correctly worn PPE as needed
            ppe_worn_count += 1
        
        # Count explicit violations and gather details
        if class_name.startswith('no-'): # Any class starting with 'no-' indicates a violation
            violations_count += 1
            violation_details.append({
                'violation_type': class_name,
                'location_box': box,
                'confidence': confidence,
                'severity': 1 # Default severity for Batch 3
            })
            
    status_message = "Compliant"
    if violations_count > 0:
        status_message = f"{violations_count} Violation(s) Detected"
    elif person_count > 0 and violations_count == 0:
        status_message = "Compliant (All persons wearing detected PPE)"
    elif person_count == 0:
        status_message = "No persons detected"


    logger.debug(f"Frame Analysis: Persons={person_count}, PPE Worn={ppe_worn_count}, Violations={violations_count}, Status='{status_message}'")
    return person_count, ppe_worn_count, violations_count, status_message, violation_details


def generate_frames(source: Union[str, int] = 0):
    """
    Generator function that continuously yields JPEG encoded frames from the video source.
    These frames are annotated with PPE detections and processed for compliance logging.
    """
    logger.info(f"Starting frame generation for source: {source}")
    
    stream = get_video_stream(source)
    if stream is None:
        logger.error(f"Cannot get video stream for source {source}. Yielding blank frames.")
        # Yield a placeholder message or error frame if stream cannot be opened
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + 
               cv2.imencode('.jpg', np.zeros((480, 640, 3), dtype=np.uint8))[1].tobytes() + # Empty black frame
               b'\r\n--frame\r\n')
        return

    if global_detector is None:
        logger.critical("PPE Detector not initialized. Cannot perform detection on stream.")
        stream.release() # Release the stream if detector is broken
        return

    frame_interval = 1.0 / (stream.get_fps() if stream.get_fps() > 0 else 30.0)
    last_frame_time = time.time()

    # --- Variables for Logging Control ---
    # Log frequency: log compliance data every N seconds or M frames
    LOG_INTERVAL_SECONDS = 5
    last_log_time = time.time()
    
    # Store aggregated info for logging if not logging every frame
    current_person_count = 0
    current_ppe_worn_count = 0
    current_violations_count = 0
    current_violation_details = []
    
    try:
        while True:
            frame = stream.read_frame()
            if frame is None:
                logger.warning("No frame received from stream. Attempting to restart or end stream.")
                break

            # Resize frame if dimensions differ
            current_width, current_height = frame.shape[1], frame.shape[0]
            if current_width != app_config.DISPLAY_WIDTH or current_height != app_config.DISPLAY_HEIGHT:
                frame = cv2.resize(frame, (app_config.DISPLAY_WIDTH, app_config.DISPLAY_HEIGHT), 
                                   interpolation=cv2.INTER_AREA)

            detections = global_detector.detect(frame)
            annotated_frame = global_detector.draw_detections(frame, detections)

            # --- Frame Analysis and Logging ---
            person_count, ppe_worn_count, violations_count, status_message, violation_details = \
                analyze_frame_for_ppe_status(detections)
            
            # Aggregate data if logging periodically (e.g., take the last frame's status)
            current_person_count = person_count
            current_ppe_worn_count = ppe_worn_count
            current_violations_count = violations_count
            current_violation_details = violation_details # Store for logging if a violation occurred

            # Log compliance and violations periodically
            current_time = time.time()
            if (current_time - last_log_time) >= LOG_INTERVAL_SECONDS:
                logger.debug(f"Attempting to log data. Time since last log: {current_time - last_log_time:.2f}s")
                with current_app.app_context(): # Ensure DB operations run in app context
                    log_id = db_manager.save_compliance_log(
                        person_count=current_person_count,
                        ppe_worn_count=current_ppe_worn_count,
                        violations_count=current_violations_count,
                        status=status_message
                    )
                    if log_id is not None and current_violations_count > 0:
                        for detail in current_violation_details:
                            db_manager.save_violation_event(
                                log_id=log_id,
                                violation_type=detail['violation_type'],
                                location_box=detail['location_box'],
                                confidence=detail['confidence'],
                                severity=detail['severity']
                            )
                    elif log_id is None:
                        logger.error("Failed to save compliance log, skipping violation event logging for this interval.")
                last_log_time = current_time # Reset timer after logging


            # Encode and yield frame for web display
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
        # The stream is globally managed; do not release here to allow other clients to connect
        # if using a single global stream. For robust multi-user, each would have its own stream.
        # For this demo, _current_video_stream is only released when source changes via get_video_stream.
        pass # Stream managed by get_video_stream, not released per generator instance

@web_routes.route('/video_feed')
def video_feed():
    """
    Provides the real-time video feed for the web dashboard.
    """
    logger.info("Video feed requested.")
    # Default to camera 0. Future batches might allow selection.
    return Response(generate_frames(source=0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')