import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file at the very start
load_dotenv(override=True)

# Define application data directory (for logs, DB, snapshots, heatmaps)
APP_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app_data')
os.makedirs(APP_DATA_DIR, exist_ok=True) # Ensure the directory exists

LOG_FILE_PATH = os.path.join(APP_DATA_DIR, "app_log.log")

# Configure logging for the entire application.
logging.basicConfig(
    level=logging.INFO,  # Default level for general messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__) # Logger for this config module

class Config:
    """
    Configuration class for the InjuryShield PPE Detection System.
    Manages global settings, paths, thresholds, and various system behaviors.
    """

    # Flask Secret Key for session management.
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'a_very_long_and_complex_secret_key_for_development_purposes_only_change_me_in_production')
    
    # --- Database Configuration ---
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{APP_DATA_DIR}/injuryshield.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    logger.debug(f"Database URI: {SQLALCHEMY_DATABASE_URI}")

    # --- Paths and File Locations ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # This is 'app/' directory
    PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR)) # Go up two levels from 'app'
    MODELS_DIR = os.path.join(PROJECT_ROOT_DIR, 'models')
    YOLOV8_MODEL_PATH = os.path.join(MODELS_DIR, 'yolov8n.pt')
    PPE_CUSTOM_MODEL_PATH = os.path.join(MODELS_DIR, 'ppe_custom.pt')
    CLASS_NAMES_FILE = "C:/Users/AI/Documents/InjuryShield/models/classes.txt"

    # Path to store saved snapshots of violation frames.
    SNAPSHOTS_DIR = os.path.join(PROJECT_ROOT_DIR, 'static', 'snapshots')
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True) # Ensure snapshots directory exists
    logger.debug(f"Snapshots directory: {SNAPSHOTS_DIR}")

    # Path to store generated heatmap images.
    HEATMAP_OUTPUT_DIR = os.path.join(PROJECT_ROOT_DIR, 'static', 'reports')
    os.makedirs(HEATMAP_OUTPUT_DIR, exist_ok=True) # Ensure reports directory exists
    logger.debug(f"Heatmap output directory: {HEATMAP_OUTPUT_DIR}")


    # --- Detection Thresholds ---
    CONFIDENCE_THRESHOLD = 0.50
    IOU_THRESHOLD = 0.45

    # --- Display Settings ---
    DISPLAY_WIDTH = 1280
    DISPLAY_HEIGHT = 720
    
    # --- Alerting Configuration ---
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    ALERT_RECIPIENT_PHONE_NUMBER = os.getenv('ALERT_RECIPIENT_PHONE_NUMBER')
    ALERT_COOLDOWN_SECONDS = 60 # Cooldown period for alerts (e.g., 60 seconds per violation type)

    # --- Logging and Snapshot Settings ---
    LOG_INTERVAL_SECONDS = 5 # How often to log compliance status to DB
    # Enable/disable saving frame snapshots on violation.
    SAVE_VIOLATION_SNAPSHOT = True 
    # Percentage of frames with violation before taking a snapshot (e.g. 0.2 means 20% of consecutive violations)
    SNAPSHOT_TRIGGER_THRESHOLD = 0.1 # Minimum confidence for a detection to trigger a snapshot
    SNAPSHOT_CONSECUTIVE_VIOLATIONS = 5 # Number of consecutive violations to trigger a snapshot


    # --- Analytics Configuration ---
    HEATMAP_RESOLUTION = (640, 480) # Resolution of the generated heatmap image
    HEATMAP_MAX_DATA_POINTS = 5000 # Max violation points to consider for heatmap to prevent lag

    logger.info("Configuration loaded successfully.")

# Instatiate the config object
app_config = Config()