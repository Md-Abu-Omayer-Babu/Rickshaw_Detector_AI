import cv2
import numpy as np
from typing import Tuple
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

# Colors for entry/exit lines
LINE_COLOR_ENTRY = (0, 255, 0)   # Green for entry line
LINE_COLOR_EXIT = (0, 0, 255)     # Red for exit line
LINE_COLOR_DEFAULT = (255, 255, 0) # Yellow for default line


def draw_detections(
    image: np.ndarray,
    detection_result: DetectionResult,
    detector: YOLODetector,
    thickness: int = 2,
    font_scale: float = 0.6
) -> np.ndarray:
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


def draw_entry_exit_line(
    image: np.ndarray,
    line_start: Tuple[int, int],
    line_end: Tuple[int, int],
    color: Tuple[int, int, int] = LINE_COLOR_DEFAULT,
    thickness: int = 3,
    label: str = "Counting Line"
) -> np.ndarray:
    output_image = image.copy()
    
    # Draw the main line
    cv2.line(output_image, line_start, line_end, color, thickness)
    
    # Draw circles at endpoints
    cv2.circle(output_image, line_start, 5, color, -1)
    cv2.circle(output_image, line_end, 5, color, -1)
    
    # Draw label near the line
    label_pos = (
        (line_start[0] + line_end[0]) // 2,
        (line_start[1] + line_end[1]) // 2 - 10
    )
    
    # Calculate label size for background
    (label_width, label_height), baseline = cv2.getTextSize(
        label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
    )
    
    # Draw label background
    cv2.rectangle(
        output_image,
        (label_pos[0] - 5, label_pos[1] - label_height - 5),
        (label_pos[0] + label_width + 5, label_pos[1] + 5),
        (0, 0, 0),
        -1
    )
    
    # Draw label text
    cv2.putText(
        output_image,
        label,
        label_pos,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2
    )
    
    return output_image


def draw_entry_exit_counts(
    image: np.ndarray,
    entry_count: int,
    exit_count: int,
    net_count: int,
    position: Tuple[int, int] = (10, 40),
    font_scale: float = 0.8,
    thickness: int = 2
) -> np.ndarray:
    output_image = image.copy()
    
    # Create text lines
    texts = [
        f"Entry: {entry_count}",
        f"Exit: {exit_count}",
        f"Net: {net_count}"
    ]
    
    colors = [
        (0, 255, 0),  # Green for entry
        (0, 0, 255),  # Red for exit
        (255, 255, 255)  # White for net
    ]
    
    # Draw each line
    y_offset = position[1]
    for text, color in zip(texts, colors):
        # Calculate text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )
        
        # Draw background
        padding = 8
        cv2.rectangle(
            output_image,
            (position[0] - padding, y_offset - text_height - padding),
            (position[0] + text_width + padding, y_offset + baseline + padding),
            (0, 0, 0),
            -1
        )
        
        # Draw text
        cv2.putText(
            output_image,
            text,
            (position[0], y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness
        )
        
        y_offset += text_height + baseline + padding + 5
    
    return output_image


def draw_tracked_objects(
    image: np.ndarray,
    tracked_objects: dict,
    color: Tuple[int, int, int] = (255, 0, 255),
    thickness: int = 2
) -> np.ndarray:
    output_image = image.copy()
    
    for track_id, bbox in tracked_objects.items():
        x1, y1, x2, y2 = bbox.astype(int)
        
        # Draw bounding box
        cv2.rectangle(output_image, (x1, y1), (x2, y2), color, thickness)
        
        # Draw track ID
        label = f"ID: {track_id}"
        cv2.putText(
            output_image,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )
    
    return output_image
