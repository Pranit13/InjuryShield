# InjuryShield API Documentation

This document describes the internal and external API endpoints and core modules of the InjuryShield application, primarily for developers and system integrators.

## 1. Application Architecture Overview

InjuryShield follows a modular Flask-based architecture.

*   **`main.py`**: Entry point for the Flask application.
*   **`app/__init__.py`**: Flask app factory, initialization of SQLAlchemy, and global PPE Detector.
*   **`app/config.py`**: Centralized configuration management (paths, thresholds, credentials).
*   **`app/routes.py`**: Defines all web routes (`/`, `/history`, `/video_feed`, `/api/realtime_metrics`).
*   **`app/models.py`**: SQLAlchemy ORM models for database entities (`ComplianceLog`, `ViolationEvent`).
*   **`app/database/db_manager.py`**: Module for all database CRUD operations.
*   **`app/detection/detector.py`**: Encapsulates YOLOv8 model loading, inference, and drawing.
*   **`app/detection/video_stream.py`**: Handles video input (camera, file).
*   **`app/alerts/sms_notifier.py`**: Twilio API integration for SMS.
*   **`app/alerts/alert_logic.py`**: Manages alert triggering, cooldowns, and message formatting.
*   **`app/analytics/data_processor.py`**: Aggregates and processes historical data for insights.
*   **`app/analytics/heatmap_generator.py`**: Generates visual heatmaps.
*   **`static/`**: Static web assets (CSS, JS, images, snapshots, reports).
*   **`templates/`**: Jinja2 HTML templates.

## 2. Core Modules and Classes

### 2.1 `PPEDetector` (`app.detection.detector`)

*   **Class:** `PPEDetector`
*   **Purpose:** Handles the core computer vision task of PPE detection using YOLOv8.
*   **Methods:**
    *   `__init__(model_path, class_names_file, confidence_threshold, iou_threshold)`: Initializes the detector, loads model and class names.
    *   `detect(frame: np.ndarray) -> List[Dict]`: Performs inference on a single frame. Returns a list of dictionaries, each with 'box', 'confidence', 'class_name'.
    *   `draw_detections(frame: np.ndarray, detections: List[Dict]) -> np.ndarray`: Annotates the frame with bounding boxes and labels.

### 2.2 `VideoStream` (`app.detection.video_stream`)

*   **Class:** `VideoStream`
*   **Purpose:** Abstract layer for handling various video input sources (camera, file, image).
*   **Methods:**
    *   `__init__(source: Union[str, int])`: Initializes with video source.
    *   `open() -> bool`: Opens the video stream.
    *   `read_frame() -> Optional[np.ndarray]`: Reads a single frame.
    *   `release()`: Releases the video stream resources.
    *   `get_fps() -> float`: Returns frames per second.
    *   `get_frame_dimensions() -> Tuple[int, int]`: Returns frame width and height.

### 2.3 `DBManager` (`app.database.db_manager`)

*   **Class:** `DBManager` (static methods)
*   **Purpose:** Manages all database read/write operations for `ComplianceLog` and `ViolationEvent` models.
*   **Methods:**
    *   `initialize_database()`: Creates tables if they don't exist.
    *   `save_compliance_log(...) -> Optional[int]`: Saves a new overall compliance log entry.
    *   `save_violation_event(...) -> Optional[int]`: Saves a new specific violation event.
    *   `get_all_compliance_logs(...) -> List[Dict]`: Retrieves compliance history.
    *   `get_all_violation_events(...) -> List[Dict]`: Retrieves all violation incidents.
    *   `get_violation_coordinates(...) -> List[Tuple[int, int]]`: Fetches violation locations for heatmap.
    *   `get_compliance_metrics_last_24_hours(...) -> Dict`: Calculates aggregated metrics.

### 2.4 `SMSNotifier` (`app.alerts.sms_notifier`)

*   **Class:** `SMSNotifier`
*   **Purpose:** Provides an interface to send SMS alerts via Twilio.
*   **Methods:**
    *   `__init__()`: Initializes Twilio client with credentials.
    *   `send_sms(message_body: str) -> bool`: Sends the SMS.

### 2.5 `AlertManager` (`app.alerts.alert_logic`)

*   **Class:** `AlertManager`
*   **Purpose:** Implements logic for managing alert frequency and formatting messages.
*   **Methods:**
    *   `__init__(alert_cooldown_seconds)`: Initializes with cooldown period.
    *   `should_send_alert(violation_type: str) -> bool`: Checks if an alert can be sent.
    *   `record_alert_sent(violation_type: str)`: Resets cooldown for a type.
    *   `format_alert_message(violation_details: List[Dict], frame_time: datetime.datetime) -> str`: Formats alert text.

### 2.6 `DataProcessor` (`app.analytics.data_processor`)

*   **Class:** `DataProcessor`
*   **Purpose:** Processes raw compliance data into meaningful trends and summaries.
*   **Methods:**
    *   `get_hourly_violation_trends(...) -> Dict`: Summarizes violations by hour.
    *   `get_daily_compliance_summary(...) -> List[Dict]`: Provides day-by-day compliance.
    *   `get_violation_type_distribution(...) -> Dict`: Counts occurrences of each violation type.

### 2.7 `HeatmapGenerator` (`app.analytics.heatmap_generator`)

*   **Class:** `HeatmapGenerator`
*   **Purpose:** Generates visual heatmaps from violation coordinates.
*   **Methods:**
    *   `__init__(resolution)`: Initializes with output resolution.
    *   `generate_heatmap(violation_coords, output_path, frame_dims) -> Optional[str]`: Creates and saves the heatmap image.

## 3. Web API Endpoints

### 3.1 `/` (GET)

*   **Purpose:** Renders the main live dashboard page.
*   **Template:** `index.html`

### 3.2 `/history` (GET)

*   **Purpose:** Renders the historical reports page, including tables and analytics charts (heatmap, trends).
*   **Template:** `history.html`
*   **Data Provided:** `compliance_logs`, `violation_events`, `heatmap_url`, `hourly_trends`, `daily_summary`, `violation_type_dist`.

### 3.3 `/video_feed` (GET)

*   **Purpose:** Provides a continuous MJPEG video stream with real-time PPE detections.
*   **MIME Type:** `multipart/x-mixed-replace; boundary=frame`
*   **Return:** JPEG-encoded frames.

### 3.4 `/api/realtime_metrics` (GET)

*   **Purpose:** REST API endpoint to fetch aggregated compliance metrics for the last 24 hours. Used by the dashboard's JavaScript for dynamic updates.
*   **Return:** JSON object with metrics like `total_persons_24h`, `total_violations_24h`, `compliance_rate_24h`, `total_logs_24h`.

## 4. Configuration (`app/config.py`)

All global parameters are managed in `app/config.py` and sourced from `.env` where appropriate. Key parameters include:

*   `SECRET_KEY`
*   `SQLALCHEMY_DATABASE_URI`
*   `YOLOV8_MODEL_PATH`, `CLASS_NAMES_FILE`
*   `CONFIDENCE_THRESHOLD`, `IOU_THRESHOLD`
*   `SNAPSHOTS_DIR`, `HEATMAP_OUTPUT_DIR`
*   `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `ALERT_RECIPIENT_PHONE_NUMBER`
*   `ALERT_COOLDOWN_SECONDS`
*   `LOG_INTERVAL_SECONDS`
*   `SAVE_VIOLATION_SNAPSHOT`, `SNAPSHOT_CONSECUTIVE_VIOLATIONS`
*   `HEATMAP_RESOLUTION`, `HEATMAP_MAX_DATA_POINTS`

## 5. Error Handling and Logging

The application utilizes Python's standard `logging` module.
*   Logs are output to the console and saved to `app_data/app_log.log`.
*   Critical errors are raised to stop application if core components fail to initialize.
*   Specific try-except blocks are implemented in various modules for robust operation.