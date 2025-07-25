import logging
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from typing import List, Tuple, Optional
import os
import datetime

from app.config import app_config

# Get a logger for the heatmap generator module
logger = logging.getLogger(__name__)

class HeatmapGenerator:
    """
    Generates a heatmap image based on violation coordinates.
    The heatmap visually represents areas with higher concentrations of PPE violations.
    """

    def __init__(self, resolution: Tuple[int, int] = app_config.HEATMAP_RESOLUTION):
        """
        Initializes the HeatmapGenerator.

        Args:
            resolution (Tuple[int, int]): The (width, height) of the generated heatmap image.
        """
        self.resolution = resolution
        logger.info(f"HeatmapGenerator initialized with resolution: {self.resolution}")

    def generate_heatmap(self, 
                         violation_coords: List[Tuple[int, int]],
                         output_path: str,
                         frame_dims: Optional[Tuple[int, int]] = None) -> Optional[str]:
        """
        Generates and saves a heatmap image based on a list of violation coordinates.

        Args:
            violation_coords (List[Tuple[int, int]]): A list of (x, y) coordinates
                                                      representing violation locations.
            output_path (str): The full path including filename where the heatmap image will be saved.
            frame_dims (Optional[Tuple[int, int]]): Original frame dimensions (width, height) if coordinates
                                                    need to be scaled to the heatmap resolution.
                                                    If None, assumes coords are already scaled or direct.

        Returns:
            Optional[str]: The path to the saved heatmap image if successful, None otherwise.
        """
        logger.info(f"Generating heatmap with {len(violation_coords)} points.")

        # Create an empty 2D array (grid) to accumulate violation counts
        heatmap_data = np.zeros((self.resolution[1], self.resolution[0]), dtype=np.float32) # height, width

        if not violation_coords:
            logger.warning("No violation coordinates provided for heatmap generation. Returning empty heatmap.")
            # Create a blank image if no data
            plt.figure(figsize=(self.resolution[0]/100, self.resolution[1]/100), dpi=100) # Use dpi for actual size
            plt.imshow(np.zeros((self.resolution[1], self.resolution[0]), dtype=np.uint8), cmap='gray')
            plt.axis('off')
            plt.title("No Violation Data Available", fontsize=10)
            plt.tight_layout()
            try:
                plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
                plt.close()
                return output_path
            except Exception as e:
                logger.error(f"Failed to save blank heatmap to {output_path}: {e}")
                plt.close()
                return None


        # Scale coordinates if original frame dimensions are provided and differ from heatmap resolution
        scale_x, scale_y = 1.0, 1.0
        if frame_dims and (frame_dims[0] != self.resolution[0] or frame_dims[1] != self.resolution[1]):
            scale_x = self.resolution[0] / frame_dims[0]
            scale_y = self.resolution[1] / frame_dims[1]
            logger.debug(f"Scaling coordinates from {frame_dims} to {self.resolution} (scales: {scale_x:.2f}, {scale_y:.2f})")
        else:
            logger.debug("Coordinates not scaled (frame_dims not provided or match heatmap resolution).")


        # Populate the heatmap data array
        for x, y in violation_coords:
            # Apply scaling
            scaled_x = int(x * scale_x)
            scaled_y = int(y * scale_y)

            # Ensure coordinates are within bounds
            if 0 <= scaled_x < self.resolution[0] and 0 <= scaled_y < self.resolution[1]:
                heatmap_data[scaled_y, scaled_x] += 1
            else:
                logger.debug(f"Skipping out-of-bounds coordinate: ({x},{y}) -> ({scaled_x},{scaled_y}) for resolution {self.resolution}")

        # Apply Gaussian blur for smoothing the heatmap
        # This makes hotspots spread out and look more natural.
        heatmap_data = cv2.GaussianBlur(heatmap_data, (15, 15), 0) # Kernel size 15x15, sigmaX 0

        # Normalize data to [0, 1] for color mapping
        max_val = np.max(heatmap_data)
        if max_val > 0:
            heatmap_data = heatmap_data / max_val
        else:
            logger.warning("Heatmap data is all zeros after processing. No hotspots detected.")
            # If all zeros, it means no meaningful accumulation, so return blank
            return self.generate_heatmap([], output_path, frame_dims=frame_dims) # Call itself to create a blank heatmap

        # Define a custom colormap for better visualization
        # From transparent to red/yellow for hotspots
        colors = [(0, 0, 0, 0),    # Transparent black
                  (0, 0, 1, 0.2),  # Blue (low intensity)
                  (0, 1, 1, 0.4),  # Cyan
                  (1, 1, 0, 0.6),  # Yellow
                  (1, 0, 0, 0.8)]  # Red (high intensity)
        cmap = LinearSegmentedColormap.from_list("custom_heatmap", colors, N=256)

        # Plotting the heatmap using Matplotlib
        plt.figure(figsize=(self.resolution[0]/100, self.resolution[1]/100), dpi=100) # Ensure figure size matches resolution
        plt.imshow(heatmap_data, cmap=cmap, origin='upper', extent=[0, self.resolution[0], self.resolution[1], 0])
        
        plt.axis('off') # Hide axes
        plt.margins(0,0) # No extra margins
        plt.gca().set_position([0, 0, 1, 1]) # Make plot fill the entire figure area

        try:
            plt.savefig(output_path, transparent=True, bbox_inches='tight', pad_inches=0)
            logger.info(f"Heatmap saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save heatmap to {output_path}: {e}", exc_info=True)
            return None
        finally:
            plt.close() # Close the plot to free memory

heatmap_generator = HeatmapGenerator()