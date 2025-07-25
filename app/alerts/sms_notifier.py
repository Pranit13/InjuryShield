import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.config import app_config

# Get a logger for the SMS Notifier module
logger = logging.getLogger(__name__)

class SMSNotifier:
    """
    Handles sending SMS notifications using the Twilio API.
    Initializes the Twilio client with credentials from app_config.
    """

    def __init__(self):
        """
        Initializes the Twilio client. Checks if Twilio credentials are provided.
        """
        self.account_sid = app_config.TWILIO_ACCOUNT_SID
        self.auth_token = app_config.TWILIO_AUTH_TOKEN
        self.twilio_phone_number = app_config.TWILIO_PHONE_NUMBER
        self.recipient_phone_number = app_config.ALERT_RECIPIENT_PHONE_NUMBER

        if not all([self.account_sid, self.auth_token, self.twilio_phone_number, self.recipient_phone_number]):
            logger.warning("Twilio credentials or phone numbers not fully configured. SMS alerts will be disabled.")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}. SMS alerts will be disabled.", exc_info=True)
                self.client = None

    def send_sms(self, message_body: str) -> bool:
        """
        Sends an SMS message to the configured recipient phone number.

        Args:
            message_body (str): The text content of the SMS message.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        if self.client is None:
            logger.warning("Twilio client not initialized. Cannot send SMS.")
            return False

        if not self.recipient_phone_number:
            logger.error("Recipient phone number is not configured. Cannot send SMS.")
            return False

        if not self.twilio_phone_number:
            logger.error("Twilio phone number is not configured. Cannot send SMS.")
            return False

        try:
            # Create a message. 'to' is the recipient, 'from_' is your Twilio number.
            message = self.client.messages.create(
                to=self.recipient_phone_number,
                from_=self.twilio_phone_number,
                body=message_body
            )
            logger.info(f"SMS sent successfully! SID: {message.sid}")
            return True
        except TwilioRestException as e:
            # Catch specific Twilio API errors (e.g., invalid phone number, authentication failure)
            logger.error(f"Twilio API error sending SMS: {e.msg}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending SMS: {e}", exc_info=True)
            return False

# Instantiate the SMSNotifier globally for easy access throughout the application.
sms_notifier = SMSNotifier()