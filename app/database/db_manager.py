import logging
import datetime
from typing import List, Dict, Optional, Any, Tuple

from flask import current_app
from app.extensions import db
from app.models import ComplianceLog, ViolationEvent

logger = logging.getLogger(__name__)

class DBManager:
    """
    Manages all interactions with the application's database.
    Provides methods for saving compliance logs and violation events,
    as well as retrieving historical data and data for analytics.
    """

    @staticmethod
    def initialize_database():
        """
        Initializes the database by creating all defined tables.
        This method should be called within a Flask application context.
        """
        try:
            db.create_all()
            logger.info("Database tables initialized (checked/created).")
        except Exception as e:
            logger.critical(f"Failed to initialize database tables: {e}", exc_info=True)
            raise RuntimeError("Database initialization failed.")

    @staticmethod
    def save_compliance_log(
        person_count: int,
        ppe_worn_count: int,
        violations_count: int,
        frame_snapshot_path: Optional[str] = None,
        status: str = 'Unknown'
    ) -> Optional[int]:
        """
        Saves a new compliance log entry to the database.

        Args:
            person_count (int): Number of persons detected in the frame.
            ppe_worn_count (int): Number of PPE items worn correctly.
            violations_count (int): Number of distinct violations detected.
            frame_snapshot_path (Optional[str]): Path to a saved image snapshot of the frame.
            status (str): Overall compliance status of the frame (e.g., 'Compliant', 'Violations').

        Returns:
            Optional[int]: The ID of the newly created ComplianceLog entry, or None on failure.
        """
        try:
            new_log = ComplianceLog(
                person_count=person_count,
                ppe_worn_count=ppe_worn_count,
                violations_count=violations_count,
                frame_snapshot_path=frame_snapshot_path,
                status=status
            )
            db.session.add(new_log)
            db.session.commit()
            logger.info(f"Saved new compliance log: ID {new_log.id}, Persons: {person_count}, Violations: {violations_count}")
            return new_log.id
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving compliance log: {e}", exc_info=True)
            return None

    @staticmethod
    def save_violation_event(
        log_id: int,
        violation_type: str,
        location_box: Optional[List[int]] = None,
        confidence: Optional[float] = None,
        severity: int = 1
    ) -> Optional[int]:
        """
        Saves a new PPE violation event entry to the database.

        Args:
            log_id (int): The ID of the parent ComplianceLog entry.
            violation_type (str): Type of violation (e.g., 'no-helmet', 'no-vest').
            location_box (Optional[List[int]]): Bounding box coordinates [x1, y1, x2, y2] of the violation.
            confidence (Optional[float]): Confidence score of the detection.
            severity (int): Severity level of the violation (1-5).

        Returns:
            Optional[int]: The ID of the newly created ViolationEvent entry, or None on failure.
        """
        try:
            loc_box_str = str(location_box) if location_box else None

            new_event = ViolationEvent(
                log_id=log_id,
                violation_type=violation_type,
                location_box=loc_box_str,
                confidence=confidence,
                severity=severity
            )
            db.session.add(new_event)
            db.session.commit()
            logger.info(f"Saved new violation event: Log ID {log_id}, Type '{violation_type}'")
            return new_event.id
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving violation event: {e}", exc_info=True)
            return None

    @staticmethod
    def get_all_compliance_logs(limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves recent compliance log entries from the database, ordered by timestamp.
        """
        try:
            logs = ComplianceLog.query.order_by(ComplianceLog.timestamp.desc()).limit(limit).all()
            logger.debug(f"Retrieved {len(logs)} compliance logs.")
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"Error retrieving compliance logs: {e}", exc_info=True)
            return []

    @staticmethod
    def get_violations_for_log(log_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all violation events associated with a specific compliance log ID.
        """
        try:
            events = ViolationEvent.query.filter_by(log_id=log_id).all()
            logger.debug(f"Retrieved {len(events)} violations for log ID {log_id}.")
            return [event.to_dict() for event in events]
        except Exception as e:
            logger.error(f"Error retrieving violations for log {log_id}: {e}", exc_info=True)
            return []

    @staticmethod
    def get_all_violation_events(limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves recent individual violation events from the database, ordered by timestamp.
        """
        try:
            events = ViolationEvent.query.order_by(ViolationEvent.timestamp.desc()).limit(limit).all()
            logger.debug(f"Retrieved {len(events)} individual violation events.")
            return [event.to_dict() for event in events]
        except Exception as e:
            logger.error(f"Error retrieving all violation events: {e}", exc_info=True)
            return []

    @staticmethod
    def get_violation_coordinates(start_date: Optional[datetime.datetime] = None, 
                                  end_date: Optional[datetime.datetime] = None,
                                  max_points: int = 5000) -> List[Tuple[int, int]]:
        """
        Retrieves the center coordinates of bounding boxes for all violation events
        within a specified date range. Used for heatmap generation.

        Args:
            start_date (Optional[datetime.datetime]): Start timestamp for filtering.
            end_date (Optional[datetime.datetime]): End timestamp for filtering.
            max_points (int): Maximum number of violation points to retrieve.

        Returns:
            List[Tuple[int, int]]: A list of (x_center, y_center) tuples for violations.
        """
        try:
            query = ViolationEvent.query
            if start_date:
                query = query.filter(ViolationEvent.timestamp >= start_date)
            if end_date:
                query = query.filter(ViolationEvent.timestamp <= end_date)
            
            # Order by timestamp and limit to prevent too many points for heatmap
            events = query.order_by(ViolationEvent.timestamp.desc()).limit(max_points).all()
            
            coordinates = []
            for event in events:
                if event.location_box:
                    try:
                        # Convert string "[x1,y1,x2,y2]" back to list of ints
                        box = list(map(int, event.location_box.strip('[]').split(',')))
                        if len(box) == 4:
                            x1, y1, x2, y2 = box
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                            coordinates.append((center_x, center_y))
                    except ValueError:
                        logger.warning(f"Could not parse location_box for event ID {event.id}: {event.location_box}")
            logger.info(f"Retrieved {len(coordinates)} violation coordinates for analytics.")
            return coordinates
        except Exception as e:
            logger.error(f"Error retrieving violation coordinates: {e}", exc_info=True)
            return []

    @staticmethod
    def get_compliance_metrics_last_24_hours() -> Dict[str, Any]:
        """
        Calculates aggregate compliance metrics (total persons, violations) over the last 24 hours.
        """
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(hours=24)

        try:
            # Query for compliance logs in the last 24 hours
            logs = ComplianceLog.query.filter(
                ComplianceLog.timestamp >= start_time,
                ComplianceLog.timestamp <= end_time
            ).all()

            total_persons = sum(log.person_count for log in logs)
            total_violations = sum(log.violations_count for log in logs)
            
            compliance_rate = 100.0
            if total_persons > 0:
                # Simple compliance rate: (Total Persons - Total Violations) / Total Persons
                # This needs refinement for actual "compliance rate per person-hour" in a real system.
                compliance_rate = ((total_persons - total_violations) / total_persons) * 100
                compliance_rate = max(0, compliance_rate) # Ensure it doesn't go below 0

            metrics = {
                'total_logs_24h': len(logs),
                'total_persons_24h': total_persons,
                'total_violations_24h': total_violations,
                'compliance_rate_24h': round(compliance_rate, 2)
            }
            logger.info(f"Calculated 24h compliance metrics: {metrics}")
            return metrics

        except Exception as e:
            logger.error(f"Error calculating 24h compliance metrics: {e}", exc_info=True)
            return {
                'total_logs_24h': 0,
                'total_persons_24h': 0,
                'total_violations_24h': 0,
                'compliance_rate_24h': 0.0
            }


db_manager = DBManager()