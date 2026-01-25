import cv2
import numpy as np
from pathlib import Path
from fastapi import UploadFile
from app.model.detector import YOLODetector
from app.utils.draw_utils import draw_detections, draw_count_overlay
from app.utils.file_utils import generate_unique_filename, save_upload_file, get_output_url
from app.db.database import insert_detection
from app.core.config import settings


class InferenceService:
    def __init__(self, detector: YOLODetector):
        self.detector = detector
    
    async def process_image(self, file: UploadFile) -> dict:
        # Generate unique filename
        output_filename = generate_unique_filename(file.filename)
        
        # Create temporary path for uploaded file
        temp_path = settings.images_output_dir / f"temp_{output_filename}"
        
        try:
            # Save uploaded file temporarily
            await save_upload_file(file, temp_path)
            
            # Read image
            image = cv2.imread(str(temp_path))
            
            if image is None:
                raise ValueError("Failed to read image file")
            
            # Run detection
            detection_result = self.detector.detect(image)
            
            # Count rickshaws
            rickshaw_count = self.detector.count_rickshaws(detection_result)
            
            # Draw detections on image
            annotated_image = draw_detections(image, detection_result, self.detector)
            
            # Draw count overlay
            annotated_image = draw_count_overlay(annotated_image, rickshaw_count)
            
            # Save annotated image
            output_path = settings.images_output_dir / output_filename
            cv2.imwrite(str(output_path), annotated_image)
            
            # Remove temporary file
            if temp_path.exists():
                temp_path.unlink()
            
            # Insert record into database
            insert_detection(
                file_type="image",
                file_name=output_filename,
                rickshaw_count=rickshaw_count
            )
            
            # Generate output URL
            output_url = get_output_url(output_filename, "image")
            
            return {
                "file_name": output_filename,
                "rickshaw_count": rickshaw_count,
                "output_url": output_url
            }
            
        except Exception as e:
            # Clean up temporary file on error
            if temp_path.exists():
                temp_path.unlink()
            raise e
