import logging
import os
from flask import Flask, Blueprint
from app.extensions import db
from app.config import app_config
from app.detection.detector import PPEDetector
from app import shared

# Get a logger for the Flask application initialization
logger = logging.getLogger(__name__)

# Initialize the PPEDetector globally for the Flask application.
try:
    shared.global_detector = PPEDetector(
        model_path=app_config.YOLOV8_MODEL_PATH,
        class_names_file=app_config.CLASS_NAMES_FILE,
        confidence_threshold=app_config.CONFIDENCE_THRESHOLD,
        iou_threshold=app_config.IOU_THRESHOLD
    )
    logger.info("Global PPEDetector instance initialized successfully.")
except (FileNotFoundError, RuntimeError) as e:
    logger.critical(f"Failed to initialize global PPEDetector: {e}. Application cannot start.")
    shared.global_detector = None


def create_app() -> Flask:
    """
    Factory function to create and configure the Flask application instance.
    Initializes Flask extensions, registers blueprints, and sets up database.

    Returns:
        Flask: The configured Flask application instance.
    """
    logger.info("Creating Flask application instance.")
    app = Flask(__name__, static_folder='../static', template_folder='templates')

    # Load configuration from the Config class.
    app.config.from_object(app_config)
    logger.debug(f"Flask Secret Key set.")

    # Initialize SQLAlchemy with the Flask app.
    db.init_app(app)
    logger.info("SQLAlchemy initialized.")

    # Register blueprints.
    from app.routes import web_routes
    app.register_blueprint(web_routes)
    logger.info("Blueprint 'web_routes' registered.")

    # Import models here to ensure they are registered with SQLAlchemy
    # before calling db.create_all().
    with app.app_context():
        from app import models # This imports the models.py content and registers models
        db.create_all() # Create database tables based on models
        logger.info("Database tables checked/created.")

    logger.info("Flask application instance created successfully.")
    return app