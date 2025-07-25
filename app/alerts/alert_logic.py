import logging
import time
from typing import List, Dict, Any, Tuple
from collections import defaultdict

# Get a logger for the alert logic module
logger = logging.getLogger(__name__)

class AlertManager:
    """
    Manages the logic for triggering alerts based on detected PPE violations.
    Includes rate limiting and persistence of violation states.
    """

    def __init__(self, alert_cooldown_seconds: int = 60):
        """
        Initializes the AlertManager.

        Args:
            alert_cooldown_seconds (int): Minimum time in seconds between
                                          consecutive alerts for the same type of violation.
        """
        self.alert_cooldown_seconds = alert_cooldown_seconds
        # Stores the timestamp of the last alert sent for each violation type.
        # Format: {'no-helmet': last_sent_timestamp, 'no-vest': last_sent_timestamp, ...}
        self.last_alert_time = defaultdict(float) # Default to 0.0 (epoch start)

        logger.info(f"AlertManager initialized with cooldown: {alert_cooldown_seconds} seconds.")

    def should_send_alert(self, violation_type: str) -> bool:
        """
        Determines if an alert should be sent for a given violation type,
        considering the cooldown period.

        Args:
            violation_type (str): The type of violation (e.g., 'no-helmet').

        Returns:
            bool: True if an alert can be sent, False otherwise.
        """
        current_time = time.time()
        time_since_last_alert = current_time - self.last_alert_time[violation_type]

        if time_since_last_alert >= self.alert_cooldown_seconds:
            logger.debug(f"Cooldown passed for '{violation_type}'. Ready to send alert.")
            return True
        else:
            logger.debug(f"Cooldown active for '{violation_type}'. Remaining: {self.alert_cooldown_seconds - time_since_last_alert:.2f}s")
            return False

    def record_alert_sent(self, violation_type: str):
        """
        Records that an alert has been sent for a specific violation type,
        resetting its cooldown timer.

        Args:
            violation_type (str): The type of violation for which an alert was sent.
        """
        self.last_alert_time[violation_type] = time.time()
        logger.info(f"Recorded alert sent for '{violation_type}'. Cooldown reset.")

    def format_alert_message(self, violation_details: List[Dict[str, Any]], frame_time: datetime.datetime) -> str:
        """
        Formats a user-friendly SMS message for detected violations.

        Args:
            violation_details (List[Dict[str, Any]]): List of specific violation event details.
            frame_time (datetime.datetime): Timestamp of the frame where violations were detected.

        Returns:
            str: The formatted SMS message.
        """
        if not violation_details:
            return "No violations detected."

        message_parts = [f"InjuryShield ALERT at {frame_time.strftime('%Y-%m-%d %H:%M:%S UTC')}:"]
        
        # Aggregate violations by type for a concise message
        violation_summary = defaultdict(int)
        for detail in violation_details:
            violation_summary[detail['violation_type']] += 1
        
        for v_type, count in violation_summary.items():
            message_parts.append(f"- {count}x {v_type.replace('no-', 'missing ')}")
        
        message_parts.append("Immediate action required.")
        # You could add a link to the dashboard here in Batch 5
        # message_parts.append("View dashboard: http://your-dashboard-url")

        return "\n".join(message_parts)

# Instantiate the AlertManager globally
alert_manager = AlertManager(alert_cooldown_seconds=app_config.ALERT_COOLDOWN_SECONDS) # Cooldown from config