# InjuryShield Installation and Deployment Guide

This guide provides step-by-step instructions for installing, configuring, and deploying the InjuryShield PPE monitoring system.

## 1. System Requirements

### 1.1 Hardware Requirements

*   **Processor:** Modern multi-core CPU (Intel i5/i7/i9 8th gen or newer, AMD Ryzen 5/7/9 equivalent) for efficient real-time detection.
    *   **GPU (Recommended):** NVIDIA GPU with CUDA capabilities (e.g., GeForce RTX series, Tesla) for accelerated YOLOv8 inference. This dramatically improves performance.
*   **RAM:** Minimum 8GB, 16GB+ recommended for smoother operation, especially with multiple camera streams or higher resolutions.
*   **Storage:** 50GB+ free space (SSD recommended) for application, models, logs, and saved snapshots/reports.
*   **Camera:** IP camera (RTSP stream recommended) or USB webcam compatible with OpenCV.

### 1.2 Software Requirements

*   **Operating System:**
    *   Ubuntu 20.04+ (recommended for production deployment with CUDA)
    *   Windows 10/11
    *   macOS
*   **Python:** Python 3.8 - 3.10 (verify compatibility with `ultralytics` and `tensorflow-gpu` if used later).
*   **Pip:** Python package installer.
*   **OpenCV:** Pre-built OpenCV libraries for Python (`opencv-python`).
*   **CUDA Toolkit & cuDNN (for GPU acceleration):** Required if using an NVIDIA GPU. Must match your PyTorch/TensorFlow version.

## 2. Setup Procedure

### 2.1 Clone the Repository

First, obtain the project files:

```bash
git clone https://github.com/your-repo/InjuryShield.git # Replace with your actual repository URL
cd InjuryShield


python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate


Note: If you plan to use GPU acceleration, you might need pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 (replace cu118 with your CUDA version) before ultralytics or ensure ultralytics installs the GPU-enabled version.