from ultralytics import YOLO
import numpy as np
from typing import List, Tuple


class DetectionResult:
    def __init__(self, boxes: np.ndarray, confidences: np.ndarray, class_ids: np.ndarray):
        self.boxes = boxes
        self.confidences = confidences
        self.class_ids = class_ids
        self.count = len(boxes)
    
    def __len__(self):
        return self.count


class YOLODetector:
    def __init__(self, model_path: str, confidence: float = 0.25, iou: float = 0.45, device: str = "cpu"):
        self.model_path = model_path
        self.confidence = confidence
        self.iou = iou
        self.device = device
        
        self.model = YOLO(model_path)
        self.model.to(device)
        self.class_names = self.model.names
    
    def detect(self, image: np.ndarray) -> DetectionResult:
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
        return self.class_names.get(class_id, "unknown")
    
    def count_rickshaws(self, detection_result: DetectionResult) -> int:
        # Count all detections (assuming model is trained only for rickshaws)
        # If your model has multiple classes, you can filter by class name here
        return len(detection_result)
