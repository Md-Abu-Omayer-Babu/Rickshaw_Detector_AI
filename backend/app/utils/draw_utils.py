"""
Drawing utilities for visualizing detection results.
"""
import cv2
import numpy as np
from app.model.detector import DetectionResult, YOLODetector


# Color palette for bounding boxes (BGR format)
COLORS = [
    (0, 255, 0),      # Green
    (255, 0, 0),      # Blue
    (0, 0, 255),      # Red
    (255, 255, 0),    # Cyan
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Yellow
]


def draw_detections(
    image: np.ndarray,
    detection_result: DetectionResult,
    detector: YOLODetector,
    thickness: int = 2,
    font_scale: float = 0.6
) -> np.ndarray:
    """
    Draw bounding boxes and labels on image.
    
    Args:
        image: Input image (BGR format)
        detection_result: Detection results
        detector: YOLODetector instance for getting class names
        thickness: Line thickness for bounding boxes
        font_scale: Font scale for labels
        
    Returns:
        np.ndarray: Image with drawn bounding boxes and labels
    """
    # Create a copy to avoid modifying original
    output_image = image.copy()
    
    # Draw each detection
    for i in range(len(detection_result)):
        # Get box coordinates
        x1, y1, x2, y2 = detection_result.boxes[i].astype(int)
        
        # Get confidence and class ID
        confidence = detection_result.confidences[i]
        class_id = detection_result.class_ids[i]
        class_name = detector.get_class_name(class_id)
        
        # Select color based on class ID
        color = COLORS[class_id % len(COLORS)]
        
        # Draw bounding box
        cv2.rectangle(output_image, (x1, y1), (x2, y2), color, thickness)
        
        # Create label text
        label = f"{class_name}: {confidence:.2f}"
        
        # Calculate label size
        (label_width, label_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )
        
        # Draw label background
        cv2.rectangle(
            output_image,
            (x1, y1 - label_height - baseline - 10),
            (x1 + label_width, y1),
            color,
            -1  # Filled rectangle
        )
        
        # Draw label text
        cv2.putText(
            output_image,
            label,
            (x1, y1 - baseline - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),  # White text
            thickness
        )
    
    return output_image


def draw_count_overlay(
    image: np.ndarray,
    count: int,
    position: tuple = (10, 40),
    font_scale: float = 1.2,
    thickness: int = 3
) -> np.ndarray:
    """
    Draw rickshaw count overlay on image.
    
    Args:
        image: Input image (BGR format)
        count: Number of rickshaws detected
        position: Position to draw the text (x, y)
        font_scale: Font scale for text
        thickness: Text thickness
        
    Returns:
        np.ndarray: Image with count overlay
    """
    output_image = image.copy()
    
    # Create text
    text = f"Rickshaws: {count}"
    
    # Calculate text size
    (text_width, text_height), baseline = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
    )
    
    # Draw background rectangle
    padding = 10
    cv2.rectangle(
        output_image,
        (position[0] - padding, position[1] - text_height - padding),
        (position[0] + text_width + padding, position[1] + baseline + padding),
        (0, 0, 0),  # Black background
        -1
    )
    
    # Draw text
    cv2.putText(
        output_image,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 255, 0),  # Green text
        thickness
    )
    
    return output_image
