import datetime
import logging
from app.extensions import db
from sqlalchemy import func # For database-specific functions like NOW()

# Get a logger for the models module
logger = logging.getLogger(__name__)

class ComplianceLog(db.Model):
    """
    Database model to log overall PPE compliance status for each processed frame/time interval.
    This provides a high-level overview of safety over time.
    """
    __tablename__ = 'compliance_logs'

    id = db.Column(db.Integer, primary_key=True)
    # Timestamp when the log entry was created. Defaults to current UTC time.
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    # Count of people detected in the frame.
    person_count = db.Column(db.Integer, nullable=False, default=0)
    # Count of PPE items correctly worn (e.g., helmet worn, vest worn).
    ppe_worn_count = db.Column(db.Integer, nullable=False, default=0)
    # Count of distinct PPE violations (e.g., a person missing a helmet counts as 1 violation).
    violations_count = db.Column(db.Integer, nullable=False, default=0)
    # Optional: Path to a saved snapshot of the frame if a significant event occurred.
    frame_snapshot_path = db.Column(db.String(255), nullable=True)
    # A general status message for the frame, e.g., "Compliant", "Minor Violations".
    status = db.Column(db.String(50), nullable=False, default='Unknown')

    # Relationship to ViolationEvent: One ComplianceLog can have many ViolationEvents.
    # 'backref' creates a convenient back-reference on the ViolationEvent model to access its parent ComplianceLog.
    violation_events = db.relationship('ViolationEvent', backref='compliance_log', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return (f"<ComplianceLog id={self.id}, timestamp='{self.timestamp}', "
                f"persons={self.person_count}, ppe_worn={self.ppe_worn_count}, "
                f"violations={self.violations_count}, status='{self.status}'>")

    def to_dict(self):
        """Converts the ComplianceLog object to a dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'person_count': self.person_count,
            'ppe_worn_count': self.ppe_worn_count,
            'violations_count': self.violations_count,
            'frame_snapshot_path': self.frame_snapshot_path,
            'status': self.status
        }

class ViolationEvent(db.Model):
    """
    Database model to log specific PPE violation events.
    Each entry represents a single instance of a detected non-compliance.
    """
    __tablename__ = 'violation_events'

    id = db.Column(db.Integer, primary_key=True)
    # Foreign key linking to the ComplianceLog entry that captured this violation.
    log_id = db.Column(db.Integer, db.ForeignKey('compliance_logs.id'), nullable=False)
    # Timestamp of the violation. Duplicated from ComplianceLog for easier querying of specific violations.
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    # Type of PPE violation (e.g., 'no-helmet', 'no-vest', 'no-gloves').
    violation_type = db.Column(db.String(100), nullable=False)
    # Details about the location of the violation within the frame (e.g., bounding box coordinates).
    # Stored as a string for simplicity, can be parsed back into a list/tuple.
    location_box = db.Column(db.String(100), nullable=True) # Example: "[x1,y1,x2,y2]"
    # Confidence score of the detection that led to this violation.
    confidence = db.Column(db.Float, nullable=True)
    # Severity level of the violation (e.g., 1=minor, 5=critical). For future analytics.
    severity = db.Column(db.Integer, default=1, nullable=False)
    # Flag to indicate if this specific violation has been addressed or reviewed.
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return (f"<ViolationEvent id={self.id}, log_id={self.log_id}, "
                f"timestamp='{self.timestamp}', type='{self.violation_type}', "
                f"severity={self.severity}, resolved={self.is_resolved}>")

    def to_dict(self):
        """Converts the ViolationEvent object to a dictionary."""
        return {
            'id': self.id,
            'log_id': self.log_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'violation_type': self.violation_type,
            'location_box': self.location_box,
            'confidence': self.confidence,
            'severity': self.severity,
            'is_resolved': self.is_resolved
        }

logger.info("Database models (ComplianceLog, ViolationEvent) defined.")