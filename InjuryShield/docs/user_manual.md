# InjuryShield User Manual

## 1. Introduction to InjuryShield

InjuryShield is an AI-powered PPE (Personal Protective Equipment) monitoring system designed to enhance workplace safety in manufacturing and industrial environments. It leverages computer vision to detect PPE compliance in real-time video feeds, alerts personnel to violations, and provides historical data and analytics for safety management.

## 2. System Overview

*   **Real-time Monitoring:** Connects to existing CCTV cameras to continuously monitor PPE usage.
*   **Automated Detection:** Uses advanced deep learning (YOLOv8) to identify PPE items like helmets, safety vests, and gloves.
*   **Violation Alerts:** Sends immediate SMS notifications to designated personnel when non-compliance is detected.
*   **Historical Data Logging:** Stores compliance status and violation events in a database for review.
*   **Analytics & Reporting:** Generates insights from historical data, including compliance trends and violation hotspots (heatmaps).
*   **Web Dashboard:** Provides a user-friendly interface to view live feeds, alerts, and reports via a web browser.

## 3. Getting Started

### 3.1 Accessing the Dashboard

1.  Ensure the InjuryShield application is running.
2.  Open your web browser and navigate to the application's URL, typically `http://127.0.0.1:5000/`.

### 3.2 Dashboard Navigation

*   **Dashboard (Home):** Provides a live view from the connected camera with real-time PPE detection and a summary of recent compliance metrics.
*   **History & Reports:** Displays a detailed log of past compliance events, individual violation incidents, and analytics reports like heatmaps and trend charts.

## 4. Real-time Monitoring

The main "Dashboard" page displays a live video feed. As workers move within the camera's view, the system will draw bounding boxes around detected persons and their PPE.

*   **Green boxes/labels:** Indicate correctly worn PPE.
*   **Red boxes/labels:** Indicate missing or incorrectly worn PPE, or areas of violation.
*   **Status Message:** A message below the video stream provides a quick summary of the current compliance status.

## 5. Understanding Alerts

InjuryShield is configured to send SMS alerts for critical violations.

*   **Trigger:** Alerts are triggered when specific types of PPE non-compliance (e.g., missing helmet) are detected and persist for a configured duration.
*   **Recipient:** SMS messages are sent to the phone number configured in the system settings by the administrator.
*   **Cooldown:** To prevent spamming, alerts for the same violation type will not be sent repeatedly within a short cooldown period.

## 6. History and Reports

The "History & Reports" page is crucial for safety managers to review past performance and identify areas for improvement.

### 6.1 Compliance Overview

*   **Recent Compliance Logs:** A table showing high-level compliance data for each logged time interval, including the number of persons, PPE worn, and violations.

### 6.2 Violation Events

*   **Recent Violation Events:** A detailed table of every specific PPE violation recorded, including the timestamp, type of violation (e.g., "no-helmet"), location in the frame (bounding box coordinates), and detection confidence.

### 6.3 Analytics Reports

This section provides visual summaries of safety trends.

*   **Violation Hotspot Heatmap:** An image visualizing areas within the monitored space where violations occur most frequently. Darker/redder areas indicate higher concentrations of violations.
*   **Hourly Violation Trends:** A chart showing which hours of the day experience the most PPE violations, helping to identify peak risk times.
*   **Daily Compliance Rate:** A chart tracking the overall compliance percentage day by day, useful for observing long-term trends and the impact of safety initiatives.
*   **Violation Type Distribution:** A chart breaking down the total number of violations by type (e.g., how many "no-helmet" vs. "no-vest" incidents), helping to prioritize training or equipment needs.

## 7. Troubleshooting (Basic)

*   **No Video Feed:**
    *   Check if the camera is connected and recognized by the system.
    *   Ensure the application is running correctly in the terminal.
    *   Verify the camera index or stream URL in the system configuration (`.env` file if applicable).
*   **No Detections:**
    *   Confirm the YOLOv8 model file (`.pt`) and `classes.txt` are correctly placed in the `models/` directory.
    *   Check the `CONFIDENCE_THRESHOLD` in `app/config.py`; it might be too high.
*   **No SMS Alerts:**
    *   Verify your Twilio Account SID, Auth Token, Twilio phone number, and recipient phone number are correctly set in the `.env` file.
    *   Ensure your Twilio account has sufficient balance and is enabled for SMS.
    *   Check the `ALERT_COOLDOWN_SECONDS` in `app/config.py`; alerts might be on cooldown.
    *   Review the application logs (`app_log.log`) for Twilio API errors.
*   **No Historical Data/Reports:**
    *   Ensure the application has been running for a period while monitoring activity to collect data.
    *   Check the `LOG_INTERVAL_SECONDS` in `app/config.py` to ensure data is being logged frequently enough.
    *   Verify the database file (`injuryshield.db` in `app_data/`) exists and is growing.

For further assistance, please contact your system administrator or refer to the technical documentation.