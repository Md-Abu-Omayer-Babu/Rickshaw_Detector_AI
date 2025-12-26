"""
Video processing service for video detection.
Handles the business logic for processing videos frame by frame with YOLO.
"""
import cv2
import numpy as np
from pathlib import Path
from fastapi import UploadFile
from app.model.detector import YOLODetector
from app.utils.draw_utils import draw_detections, draw_count_overlay
from app.utils.file_utils import generate_unique_filename, save_upload_file, get_output_url
from app.db.database import insert_detection
from app.core.config import settings


class VideoService:
    """Service for processing videos."""
    
    def __init__(self, detector: YOLODetector):
        """
        Initialize video service.
        
        Args:
            detector: YOLODetector instance
        """
        self.detector = detector
    
    async def process_video(self, file: UploadFile) -> dict:
        """
        Process an uploaded video file frame by frame.
        
        Args:
            file: Uploaded video file
            
        Returns:
            dict: Detection results with file info and max rickshaw count
        """
        # Generate unique filename
        output_filename = generate_unique_filename(file.filename)
        
        # Create paths
        temp_input_path = settings.videos_output_dir / f"temp_input_{output_filename}"
        output_path = settings.videos_output_dir / output_filename
        
        try:
            # Save uploaded file temporarily
            await save_upload_file(file, temp_input_path)
            
            # Open video file
            cap = cv2.VideoCapture(str(temp_input_path))
            
            if not cap.isOpened():
                raise ValueError("Failed to open video file")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            # Process frames
            max_rickshaw_count = 0
            frame_count = 0
            
            print(f"   Processing video: {total_frames} frames at {fps} FPS")
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Run detection on frame
                detection_result = self.detector.detect(frame)
                
                # Count rickshaws in this frame
                frame_rickshaw_count = self.detector.count_rickshaws(detection_result)
                
                # Update max count
                max_rickshaw_count = max(max_rickshaw_count, frame_rickshaw_count)
                
                # Draw detections on frame
                annotated_frame = draw_detections(frame, detection_result, self.detector)
                
                # Draw count overlay
                annotated_frame = draw_count_overlay(annotated_frame, frame_rickshaw_count)
                
                # Write frame to output video
                out.write(annotated_frame)
                
                frame_count += 1
                
                # Print progress every 30 frames
                if frame_count % 30 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"   Progress: {frame_count}/{total_frames} frames ({progress:.1f}%)")
            
            # Release resources
            cap.release()
            out.release()
            
            # Remove temporary file
            if temp_input_path.exists():
                temp_input_path.unlink()
            
            print(f"   Video processing complete: {frame_count} frames processed")
            print(f"   Max rickshaw count: {max_rickshaw_count}")
            
            # Insert record into database
            insert_detection(
                file_type="video",
                file_name=output_filename,
                rickshaw_count=max_rickshaw_count
            )
            
            # Generate output URL
            output_url = get_output_url(output_filename, "video")
            
            return {
                "file_name": output_filename,
                "rickshaw_count": max_rickshaw_count,
                "output_url": output_url
            }
            
        except Exception as e:
            # Clean up temporary files on error
            if temp_input_path.exists():
                temp_input_path.unlink()
            if output_path.exists():
                output_path.unlink()
            raise e
