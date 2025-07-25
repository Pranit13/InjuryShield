import os
import cv2
import logging
import time
from app.detection.detector import PPEDetector
from app.detection.video_stream import VideoStream
from app.config import app_config # Ensure logging is configured via config import

# Get a logger for the main application script
logger = logging.getLogger(__name__)

def process_static_image(image_path: str, detector: PPEDetector):
    """
    Loads a static image, performs PPE detection, and displays the annotated image.

    Args:
        image_path (str): Path to the image file.
        detector (PPEDetector): An instance of the PPEDetector class.
    """
    logger.info(f"--- Processing Static Image: {image_path} ---")
    
    # Use VideoStream to handle image loading (it has built-in error checks)
    with VideoStream(image_path) as stream:
        if stream.is_image:
            frame = stream.read_frame()
            if frame is None:
                logger.error(f"Could not read image from {image_path}. Skipping processing.")
                return

            logger.info("Image loaded. Performing detection...")
            detections = detector.detect(frame)
            logger.info(f"Detected {len(detections)} objects in {image_path}.")

            annotated_frame = detector.draw_detections(frame, detections)

            # Display the result
            window_name = f"Detected PPE - {os.path.basename(image_path)}"
            cv2.imshow(window_name, annotated_frame)
            logger.info("Displaying annotated image. Press any key to close.")
            cv2.waitKey(0) # Wait indefinitely until a key is pressed
            cv2.destroyWindow(window_name)
            logger.info("Image display closed.")
        else:
            logger.error(f"Source {image_path} is not recognized as a static image by VideoStream.")


def process_video_file(video_path: str, detector: PPEDetector):
    """
    Processes a video file frame by frame, performs PPE detection,
    and displays the annotated video in real-time.

    Args:
        video_path (str): Path to the video file.
        detector (PPEDetector): An instance of the PPEDetector class.
    """
    logger.info(f"--- Processing Video File: {video_path} ---")
    
    # Use VideoStream context manager for automatic opening and releasing
    with VideoStream(video_path) as stream:
        if stream.is_image: # Check if it mistakenly opened as image
            logger.error(f"Source {video_path} was detected as an image. Expected a video file.")
            return

        if not stream.cap or not stream.cap.isOpened():
            logger.error(f"Failed to open video file {video_path}. Skipping processing.")
            return

        fps = stream.get_fps()
        # Calculate delay per frame to maintain approximate original video speed
        delay = int(1000 / fps) if fps > 0 else 1 # Default to 1ms if FPS is unknown

        frame_count = 0
        start_time = time.time()

        window_name = f"Detected PPE - {os.path.basename(video_path)}"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL) # Allow window resizing

        logger.info(f"Starting video processing. FPS: {fps:.2f}. Press 'q' to quit.")

        while True:
            frame = stream.read_frame()
            if frame is None:
                logger.info("End of video stream or error reading frame.")
                break # Exit loop if no more frames or error

            frame_count += 1
            
            detections = detector.detect(frame)
            annotated_frame = detector.draw_detections(frame, detections)

            cv2.imshow(window_name, annotated_frame)

            key = cv2.waitKey(delay) & 0xFF # Wait for 'delay' milliseconds or a keypress
            if key == ord('q'): # 'q' key to quit
                logger.info("'q' pressed. Stopping video processing.")
                break

        end_time = time.time()
        elapsed_time = end_time - start_time
        processed_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

        logger.info(f"Finished processing video. Total frames: {frame_count}. Processed FPS: {processed_fps:.2f}")
        cv2.destroyWindow(window_name)
        logger.info("Video display closed.")


def main():
    """
    Main function to initialize the PPE detection system and demonstrate its capabilities
    on static images and video files.
    """
    logger.info("Starting InjuryShield Batch 1 Application.")

    try:
        # Initialize the PPE detector
        detector = PPEDetector(
            model_path=app_config.YOLOV8_MODEL_PATH,
            class_names_file=app_config.CLASS_NAMES_FILE,
            confidence_threshold=app_config.CONFIDENCE_THRESHOLD,
            iou_threshold=app_config.IOU_THRESHOLD
        )
        logger.info("PPEDetector instance created successfully.")

    except (FileNotFoundError, RuntimeError) as e:
        logger.critical(f"Application setup failed: {e}. Exiting.")
        return

    # --- Demonstration on a Static Image ---
    # Ensure you have a 'sample.jpg' in the root project directory for this.
    static_image_path = 'sample.jpg'
    if os.path.exists(static_image_path):
        process_static_image(static_image_path, detector)
    else:
        logger.warning(f"Static image '{static_image_path}' not found. Skipping static image demonstration.")
        logger.info("Please place a 'sample.jpg' file in the project root to test static image detection.")

    # --- Demonstration on a Video File ---
    # Ensure you have a 'sample.mp4' in the root project directory for this.
    video_file_path = 'sample.mp4'
    if os.path.exists(video_file_path):
        process_video_file(video_file_path, detector)
    else:
        logger.warning(f"Video file '{video_file_path}' not found. Skipping video file demonstration.")
        logger.info("Please place a 'sample.mp4' file in the project root to test video detection.")

    logger.info("InjuryShield Batch 1 Application finished.")

if __name__ == "__main__":
    app.run(debug=True)