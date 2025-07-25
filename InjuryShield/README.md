# InjuryShield: AI-Powered Real-time PPE Compliance Monitoring

 <!-- Replace with a nice banner image of your dashboard -->

**InjuryShield is a comprehensive, full-stack application designed to enhance workplace safety by automating the monitoring of Personal Protective Equipment (PPE) compliance. Leveraging state-of-the-art deep learning and web technologies, this system provides real-time detection, instant alerts, and powerful analytics to create a safer industrial environment.**

This project was developed as a Capstone project, addressing the critical need for modern safety solutions in industries adopting Industry 4.0 principles.

---

##  ITable of Contents

- [Key Features](#-key-features)
- [Live Demo](#-live-demo)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Installation and Setup](#-installation-and-setup)
  - [Prerequisites](#prerequisites)
  - [Backend Setup (Python)](#backend-setup-python)
  - [Frontend Setup (HTML/CSS/JS)](#frontend-setup-htmlcssjs)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Future Work](#-future-work)
- [Contributing](#-contributing)
- [License](#-license)

---

## I Key Features

-   **Real-time Video Processing:** Ingests live video streams from standard CCTV or IP cameras using OpenCV.
-   **AI-Powered PPE Detection:** Utilizes a fine-tuned **YOLOv8** model to accurately detect multiple classes of PPE (helmets, vests, gloves) and non-compliance ('no-helmet', etc.) in real-time.
-   **Interactive Web Dashboard:** A responsive, modern user interface built with HTML, CSS, and JavaScript provides a central hub for all safety monitoring activities.
-   **Instant SMS Alerts:** Integrates the **Twilio API** to send immediate SMS notifications to designated safety personnel upon detection of critical violations.
-   **Historical Data Logging:** All compliance and violation events are logged to a persistent database (SQLite/PostgreSQL) using SQLAlchemy, creating a comprehensive audit trail.
-   **Advanced Analytics & Reporting:**
    -   Visualize compliance rates over time.
    -   Analyze violation trends by hour and type.
    -   Generate violation hotspot **heatmaps**.
    -   Exportable reports for compliance meetings and documentation.
-   **Multi-Camera Monitoring:** A dedicated "Cameras" page allows users to monitor multiple feeds in a grid or focus on a single stream.
-   **System Configuration:** An intuitive settings panel for managing alert recipients, camera sources, and other system parameters.

---


---

## I Technology Stack

The InjuryShield system is built with a modern, robust, and scalable technology stack.

### Backend

-   **Language:** Python 3.9+
-   **Web Framework:** Flask
-   **Deep Learning:** Ultralytics YOLOv8
-   **Computer Vision:** OpenCV
-   **Database:** SQLAlchemy (with SQLite for development, PostgreSQL-ready)
-   **Alerting:** Twilio REST API
-   **Environment Management:** `python-dotenv`

### Frontend

-   **Core:** HTML5, CSS3, JavaScript (ES6+)
-   **Data Visualization:** Chart.js
-   **Styling:** No frameworks, pure CSS with a focus on Flexbox, Grid, and responsive design.
-   **API Communication:** Asynchronous `fetch` API.

---

## I System Architecture

The application follows a modular, client-server architecture.

1.  **Video Input:** Standard cameras send video streams to the backend.
2.  **Flask Backend Server:**
    -   **Video Processing:** OpenCV captures frames from the stream.
    -   **AI Inference:** The YOLOv8 model processes each frame to detect PPE compliance.
    -   **Business Logic:** Analyzes detection results, logs events to the database, and triggers alerts.
    -   **REST API:** Exposes endpoints to provide data (notifications, camera feeds, analytics) to the frontend.
3.  **Database:** Stores historical data on compliance, violations, and system events.
4.  **Frontend Client:** A pure HTML/CSS/JS single-page-like application that consumes data from the backend API and provides a rich, interactive user experience.

*(For a visual representation, please refer to the System Architecture diagram in the final project report.)*

---

## I Installation and Setup

Follow these steps to set up and run the InjuryShield application on your local machine.

### Prerequisites

-   Python 3.9+ and `pip`
-   An NVIDIA GPU with CUDA installed (recommended for best performance)
-   A Twilio account with an active phone number, Account SID, and Auth Token.
-   A modern web browser (Chrome, Firefox, Safari).

### Backend Setup (Python)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/injuryshield.git
    cd injuryshield
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download YOLOv8 Model Weights:**
    Download a pre-trained model (e.g., `yolov8n.pt`) from the [Ultralytics GitHub releases](https://github.com/ultralytics/ultralytics/releases) and place it in the `models/` directory.

5.  **Configure Environment Variables:**
    -   Copy the example environment file: `cp .env.example .env`
    -   Open the `.env` file and fill in your credentials:
        ```env
        FLASK_SECRET_KEY='your_super_secret_key'
        DATABASE_URL='sqlite:///app_data/injuryshield.db' # Default
        TWILIO_ACCOUNT_SID='ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        TWILIO_AUTH_TOKEN='your_twilio_auth_token'
        TWILIO_PHONE_NUMBER='+1234567890'
        ALERT_RECIPIENT_PHONE_NUMBER='+1987654321'
        ```

### Frontend Setup (HTML/CSS/JS)

The frontend files (`.html`, `css/style.css`, `js/script.js`) are served directly by the Flask application and require no separate setup. Simply ensure they are located in the correct `templates/` and `static/` directories as per the project structure.

---

## I Running the Application

1.  **Start the Backend Server:**
    Ensure your virtual environment is activated. From the project root directory, run:
    ```bash
    python main.py
    ```
    The backend server will start, typically on `http://127.0.0.1:5000`. The first run will also create the SQLite database file.

2.  **Access the Frontend:**
    Open your web browser and navigate to:
    [**http://127.0.0.1:5000/**](http://127.0.0.1:5000/)

    You will be greeted by the `index.html` landing page. From there, you can navigate to all other sections of the application.

---

## I API Endpoints

The Flask backend exposes several RESTful API endpoints that the frontend consumes.

-   `GET /api/notifications`: Fetches a list of recent system notifications.
-   `GET /api/dashboard/analytics`: Retrieves aggregated metrics and chart data for the main dashboard.
-   `GET /api/reports/analytics`: Fetches detailed analytics data for the reports page.
-   `GET /api/history/logs`: Gets a paginated list of all historical violation and compliance events.
-   `GET /api/cameras`: Returns a list of all configured camera streams and their current status.
-   `GET /video_feed/<camera_id>`: Provides the real-time MJPEG video stream for a specific camera.

*(For detailed request/response formats, please refer to the API Documentation in the final project report.)*