import cv2
import numpy as np
import logging
import time
from typing import Iterator, Union, Tuple

# Get a logger for the video_stream module
logger = logging.getLogger(__name__)

class VideoStream:
    """
    A class to handle various video input sources, including static images,
    video files, and (in future batches) live camera feeds.
    Provides methods to open, read frames, and release the stream.
    """

    def __init__(self, source: Union[str, int]):
        """
        Initializes the VideoStream with a specified source.

        Args:
            source (Union[str, int]): Path to a video file (str), path to an image file (str),
                                      or camera index (int, e.g., 0 for default webcam).
        """
        self.source = source
        self.cap = None  # OpenCV VideoCapture object
        self.is_image = False # Flag to indicate if the source is a static image
        logger.info(f"VideoStream initialized with source: {self.source}")

    def open(self) -> bool:
        """
        Opens the video stream or loads the image.

        Returns:
            bool: True if the stream/image was successfully opened/loaded, False otherwise.
        """
        logger.info(f"Attempting to open source: {self.source}")
        if isinstance(self.source, str):
            # Check if it's an image file by common extensions
            image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')
            if self.source.lower().endswith(image_extensions):
                self.is_image = True
                try:
                    # For images, we simply read it once
                    self.current_image = cv2.imread(self.source)
                    if self.current_image is None:
                        logger.error(f"Failed to load image from {self.source}. Check path or file corruption.")
                        return False
                    logger.info(f"Successfully loaded image: {self.source}")
                    return True
                except Exception as e:
                    logger.error(f"Error loading image {self.source}: {e}")
                    return False
            else:
                # Assume it's a video file or network stream
                try:
                    self.cap = cv2.VideoCapture(self.source)
                    if not self.cap.isOpened():
                        logger.error(f"Failed to open video source {self.source}. Check path, codec, or stream availability.")
                        return False
                    logger.info(f"Successfully opened video source: {self.source}")
                    return True
                except Exception as e:
                    logger.error(f"Error opening video source {self.source}: {e}")
                    return False
        elif isinstance(self.source, int):
            # Assume it's a camera index
            try:
                self.cap = cv2.VideoCapture(self.source)
                if not self.cap.isOpened():
                    logger.error(f"Failed to open camera with index {self.source}. Camera might be in use or not available.")
                    return False
                logger.info(f"Successfully opened camera with index: {self.source}")
                return True
            except Exception as e:
                logger.error(f"Error opening camera {self.source}: {e}")
                return False
        else:
            logger.error(f"Invalid source type: {type(self.source)}. Must be string (path) or int (camera index).")
            return False

    def read_frame(self) -> Union[np.ndarray, None]:
        """
        Reads a single frame from the opened video stream or returns the loaded image.

        Returns:
            np.ndarray: The captured frame as a NumPy array, or None if no frame could be read.
        """
        if self.is_image:
            # For images, we return the stored image, mimicking a single frame from a stream.
            # In a loop, this would repeatedly return the same image.
            return self.current_image.copy() if self.current_image is not None else None

        if self.cap is None or not self.cap.isOpened():
            logger.warning("Video stream not opened. Cannot read frame.")
            return None

        try:
            ret, frame = self.cap.read()
            if not ret:
                logger.debug(f"Failed to read frame from source {self.source}. End of stream or error.")
                return None
            logger.debug(f"Successfully read frame from source {self.source}.")
            return frame
        except Exception as e:
            logger.error(f"Error reading frame from source {self.source}: {e}")
            return None

    def get_fps(self) -> float:
        """
        Returns the frames per second (FPS) of the video stream.
        Not applicable for static images.

        Returns:
            float: The FPS of the video stream, or 0.0 if not applicable/available.
        """
        if self.cap and not self.is_image:
            try:
                fps = self.cap.get(cv2.CAP_PROP_FPS)
                logger.debug(f"FPS of source {self.source}: {fps}")
                return fps if fps > 0 else 0.0
            except Exception as e:
                logger.warning(f"Could not get FPS for source {self.source}: {e}")
                return 0.0
        return 0.0

    def get_frame_dimensions(self) -> Tuple[int, int]:
        """
        Returns the width and height of frames from the video stream or image.

        Returns:
            Tuple[int, int]: (width, height) of the frames.
        """
        if self.is_image and self.current_image is not None:
            h, w = self.current_image.shape[:2]
            return w, h
        if self.cap and not self.is_image:
            try:
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                return width, height
            except Exception as e:
                logger.warning(f"Could not get frame dimensions for source {self.source}: {e}")
                return 0, 0
        return 0, 0

    def release(self):
        """
        Releases the video capture object. Essential to free up camera resources.
        """
        if self.cap is not None:
            self.cap.release()
            logger.info(f"Released video source: {self.source}")
        elif self.is_image:
            logger.info(f"No video capture to release for image source: {self.source}")
        else:
            logger.warning(f"Attempted to release a non-existent or un-opened stream for source: {self.source}")

    def __enter__(self):
        """Context manager entry point."""
        if not self.open():
            raise IOError(f"Could not open video stream source: {self.source}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point. Ensures stream is released."""
        self.release()
        if exc_type:
            logger.error(f"VideoStream exited due to an exception: {exc_val}", exc_info=True)