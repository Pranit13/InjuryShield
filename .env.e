# Flask Application Secret Key
FLASK_SECRET_KEY='335c46c7bca27e643cbdc8385a837bcdd858579c7df5c984'

# Database Configuration
# For SQLite, specify a path relative to the project root.
# Example: sqlite:///./instance/site.db (for production)
# For development, you can use a path in the project root for simplicity.
# Use a double slash after sqlite: if it's an absolute path for Windows, e.g., sqlite:///C:/path/to/db.db
DATABASE_URL='sqlite:///app_data/injuryshield.db'

# Twilio Configuration (for Batch 4, but add placeholders now)
TWILIO_ACCOUNT_SID='ACec458397022cd3944be4afa362090a2f'
TWILIO_AUTH_TOKEN='f95566acb065e280054a157b9d865bea'
TWILIO_PHONE_NUMBER='+12314272949' # Your Twilio phone number
ALERT_RECIPIENT_PHONE_NUMBER='+60177776795' # Phone number to receive alerts
