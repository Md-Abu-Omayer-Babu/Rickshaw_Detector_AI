"""
YOLO detector wrapper for rickshaw detection.
Handles model loading and inference operations.
"""
from ultralytics import YOLO
import numpy as np
from typing import List, Tuple


class DetectionResult:
    """Container for detection results."""
    
    def __init__(self, boxes: np.ndarray, confidences: np.ndarray, class_ids: np.ndarray):
        """
        Initialize detection result.
        
        Args:
            boxes: Bounding boxes in format [x1, y1, x2, y2]
            confidences: Confidence scores for each detection
            class_ids: Class IDs for each detection
        """
        self.boxes = boxes
        self.confidences = confidences
        self.class_ids = class_ids
        self.count = len(boxes)
    
    def __len__(self):
        return self.count


class YOLODetector:
    """
    YOLO detector wrapper for rickshaw detection.
    Loads model once and provides inference methods.
    """
    
    def __init__(self, model_path: str, confidence: float = 0.25, iou: float = 0.45, device: str = "cpu"):
        """
        Initialize YOLO detector.
        
        Args:
            model_path: Path to the YOLO model file (best.pt)
            confidence: Confidence threshold for detections
            iou: IoU threshold for NMS
            device: Device to run inference on ('cpu' or 'cuda')
        """
        self.model_path = model_path
        self.confidence = confidence
        self.iou = iou
        self.device = device
        
        # Load YOLO model
        print(f"   Loading model from: {model_path}")
        self.model = YOLO(model_path)
        
        # Move model to device
        self.model.to(device)
        
        # Get class names
        self.class_names = self.model.names
        print(f"   Model classes: {self.class_names}")
        print(f"   Confidence threshold: {confidence}")
        print(f"   IoU threshold: {iou}")
    
    def detect(self, image: np.ndarray) -> DetectionResult:
        """
        Run detection on a single image.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            DetectionResult: Detection results containing boxes, confidences, and class IDs
        """
        # Run inference
        results = self.model.predict(
            image,
            conf=self.confidence,
            iou=self.iou,
            verbose=False,
            device=self.device
        )
        
        # Extract results from the first (and only) image
        result = results[0]
        
        # Extract bounding boxes, confidences, and class IDs
        boxes = []
        confidences = []
        class_ids = []
        
        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                # Get box coordinates (x1, y1, x2, y2)
                xyxy = box.xyxy[0].cpu().numpy()
                boxes.append(xyxy)
                
                # Get confidence
                conf = box.conf[0].cpu().numpy()
                confidences.append(float(conf))
                
                # Get class ID
                cls = int(box.cls[0].cpu().numpy())
                class_ids.append(cls)
        
        # Convert to numpy arrays
        boxes = np.array(boxes) if boxes else np.array([]).reshape(0, 4)
        confidences = np.array(confidences) if confidences else np.array([])
        class_ids = np.array(class_ids, dtype=int) if class_ids else np.array([], dtype=int)
        
        return DetectionResult(boxes, confidences, class_ids)
    
    def get_class_name(self, class_id: int) -> str:
        """
        Get class name from class ID.
        
        Args:
            class_id: Class ID
            
        Returns:
            str: Class name
        """
        return self.class_names.get(class_id, "unknown")
    
    def count_rickshaws(self, detection_result: DetectionResult) -> int:
        """
        Count the number of rickshaws in detection results.
        Assumes rickshaw is one of the classes in the model.
        
        Args:
            detection_result: Detection results
            
        Returns:
            int: Number of rickshaws detected
        """
        # Count all detections (assuming model is trained only for rickshaws)
        # If your model has multiple classes, you can filter by class name here
        return len(detection_result)
