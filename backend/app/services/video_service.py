"""
Video processing service for video detection.
Handles the business logic for processing videos frame by frame with YOLO.
"""
import cv2
import numpy as np
import json
import threading
from pathlib import Path
from fastapi import UploadFile
from typing import Optional
from app.model.detector import YOLODetector
from app.utils.draw_utils import (
    draw_detections, draw_count_overlay, draw_entry_exit_line, 
    draw_entry_exit_counts, draw_tracked_objects
)
from app.utils.file_utils import generate_unique_filename, save_upload_file, get_output_url
from app.utils.count_utils import LineCrossingDetector, SimpleTracker
from app.db.database import insert_detection, log_rickshaw_event
from app.core.config import settings, logger
from app.services.video_job_manager import get_job_manager


class VideoService:
    """Service for processing videos with entry/exit counting."""
    
    def __init__(self, detector: YOLODetector):
        """
        Initialize video service.
        
        Args:
            detector: YOLODetector instance
        """
        self.detector = detector
    
    async def process_video(
        self, 
        file: UploadFile,
        enable_counting: bool = True,
        camera_id: str = "default"
    ) -> dict:
        """
        Process an uploaded video file frame by frame with entry/exit counting.
        
        Args:
            file: Uploaded video file
            enable_counting: Enable entry/exit counting
            camera_id: Camera identifier for logging
            
        Returns:
            dict: Detection results with file info, counts, and statistics
        """
        logger.info(f"Starting video processing: {file.filename}, counting={enable_counting}")
        
        # Generate unique filename
        output_filename = generate_unique_filename(file.filename)
        
        # Create paths
        temp_input_path = settings.videos_output_dir / f"temp_input_{output_filename}"
        output_path = settings.videos_output_dir / output_filename
        
        try:
            # Save uploaded file temporarily
            await save_upload_file(file, temp_input_path)
            logger.info(f"Video saved temporarily: {temp_input_path}")
            
            # Open video file
            cap = cv2.VideoCapture(str(temp_input_path))
            
            if not cap.isOpened():
                logger.error("Failed to open video file")
                raise ValueError("Failed to open video file")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Video properties: {width}x{height} @ {fps}fps, {total_frames} frames")
            
            # Initialize line crossing detector if counting is enabled
            line_detector = None
            tracker = None
            
            if enable_counting:
                line_detector = LineCrossingDetector(
                    line_start=settings.entry_line_start,
                    line_end=settings.entry_line_end,
                    frame_width=width,
                    frame_height=height,
                    use_percentage=True
                )
                tracker = SimpleTracker()
                logger.info("Line crossing detector initialized")
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            # Process frames
            max_rickshaw_count = 0
            frame_count = 0
            total_entry = 0
            total_exit = 0
            
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
                
                # Entry/exit counting logic
                if enable_counting and line_detector and tracker and len(detection_result) > 0:
                    # Track objects
                    tracked_objects = tracker.update(detection_result.boxes)
                    
                    # Check for line crossings
                    for track_id, bbox in tracked_objects.items():
                        event = line_detector.update(
                            object_id=str(track_id),
                            bbox=bbox,
                            frame_number=frame_count
                        )
                        
                        # Log event to database
                        if event:
                            bbox_json = json.dumps(bbox.tolist())
                            confidence = detection_result.confidences[0] if len(detection_result.confidences) > 0 else 0.0
                            
                            log_rickshaw_event(
                                event_type=event,
                                confidence=float(confidence),
                                camera_id=camera_id,
                                rickshaw_id=str(track_id),
                                frame_number=frame_count,
                                bounding_box=bbox_json,
                                crossing_line="entry_line"
                            )
                    
                    # Get current counts
                    entry_count, exit_count, net_count = line_detector.get_counts()
                    total_entry = entry_count
                    total_exit = exit_count
                    
                    # Draw line and counts
                    line_start, line_end = line_detector.get_line_pixels()
                    annotated_frame = draw_entry_exit_line(
                        annotated_frame, line_start, line_end, label="Counting Line"
                    )
                    annotated_frame = draw_entry_exit_counts(
                        annotated_frame, entry_count, exit_count, net_count
                    )
                else:
                    # Legacy mode: just draw count
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
            
            logger.info(f"Video processing complete: {frame_count} frames processed")
            logger.info(f"Max rickshaw count: {max_rickshaw_count}, Entry: {total_entry}, Exit: {total_exit}")
            
            print(f"   Video processing complete: {frame_count} frames processed")
            print(f"   Max rickshaw count: {max_rickshaw_count}")
            if enable_counting:
                print(f"   Entry: {total_entry}, Exit: {total_exit}, Net: {total_entry - total_exit}")
            
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
                "total_entry": total_entry,
                "total_exit": total_exit,
                "net_count": total_entry - total_exit,
                "output_url": output_url,
                "frames_processed": frame_count
            }
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}", exc_info=True)
            # Clean up temporary files on error
            if temp_input_path.exists():
                temp_input_path.unlink()
            if output_path.exists():
                output_path.unlink()
            raise e
    
    def process_video_with_live_preview(
        self,
        job_id: str,
        temp_input_path: Path,
        output_filename: str,
        enable_counting: bool = True,
        camera_id: str = "default"
    ):
        """
        Process video in background with live frame updates for streaming.
        This method is designed to run in a separate thread.
        
        Args:
            job_id: Unique job identifier
            temp_input_path: Path to temporary uploaded video
            output_filename: Name for the output file
            enable_counting: Enable entry/exit counting
            camera_id: Camera identifier for logging
        """
        job_manager = get_job_manager()
        output_path = settings.videos_output_dir / output_filename
        
        try:
            logger.info(f"[Job {job_id}] Starting background video processing")
            
            # Open video file
            cap = cv2.VideoCapture(str(temp_input_path))
            
            if not cap.isOpened():
                raise ValueError("Failed to open video file")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"[Job {job_id}] Video: {width}x{height} @ {fps}fps, {total_frames} frames")
            
            # Create job state
            job_manager.create_job(job_id, total_frames)
            
            # Initialize line crossing detector if counting is enabled
            line_detector = None
            tracker = None
            
            if enable_counting:
                line_detector = LineCrossingDetector(
                    line_start=settings.entry_line_start,
                    line_end=settings.entry_line_end,
                    frame_width=width,
                    frame_height=height,
                    use_percentage=True
                )
                tracker = SimpleTracker()
            
            # Create video writer for output file
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            # Process frames
            max_rickshaw_count = 0
            frame_count = 0
            total_entry = 0
            total_exit = 0
            
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
                
                # Entry/exit counting logic
                if enable_counting and line_detector and tracker and len(detection_result) > 0:
                    # Track objects
                    tracked_objects = tracker.update(detection_result.boxes)
                    
                    # Check for line crossings
                    for track_id, bbox in tracked_objects.items():
                        event = line_detector.update(
                            object_id=str(track_id),
                            bbox=bbox,
                            frame_number=frame_count
                        )
                        
                        # Log event to database
                        if event:
                            bbox_json = json.dumps(bbox.tolist())
                            confidence = detection_result.confidences[0] if len(detection_result.confidences) > 0 else 0.0
                            
                            log_rickshaw_event(
                                event_type=event,
                                confidence=float(confidence),
                                camera_id=camera_id,
                                rickshaw_id=str(track_id),
                                frame_number=frame_count,
                                bounding_box=bbox_json,
                                crossing_line="entry_line"
                            )
                    
                    # Get current counts
                    entry_count, exit_count, net_count = line_detector.get_counts()
                    total_entry = entry_count
                    total_exit = exit_count
                    
                    # Draw line and counts
                    line_start, line_end = line_detector.get_line_pixels()
                    annotated_frame = draw_entry_exit_line(
                        annotated_frame, line_start, line_end, label="Counting Line"
                    )
                    annotated_frame = draw_entry_exit_counts(
                        annotated_frame, entry_count, exit_count, net_count
                    )
                else:
                    # Legacy mode: just draw count
                    annotated_frame = draw_count_overlay(annotated_frame, frame_rickshaw_count)
                
                # Write frame to output video
                out.write(annotated_frame)
                
                frame_count += 1
                
                # *** LIVE PREVIEW: Update job manager with latest processed frame ***
                # Update every frame for smooth streaming (can be optimized to every N frames if needed)
                job_manager.update_frame(job_id, annotated_frame, frame_count)
                
                # Log progress every 30 frames
                if frame_count % 30 == 0:
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"[Job {job_id}] Progress: {frame_count}/{total_frames} ({progress:.1f}%)")
            
            # Release resources
            cap.release()
            out.release()
            
            # Remove temporary file
            if temp_input_path.exists():
                temp_input_path.unlink()
            
            logger.info(f"[Job {job_id}] Processing complete: {frame_count} frames")
            
            # Insert record into database
            insert_detection(
                file_type="video",
                file_name=output_filename,
                rickshaw_count=max_rickshaw_count
            )
            
            # Generate output URL
            output_url = get_output_url(output_filename, "video")
            
            # Mark job as completed with results
            result = {
                "file_name": output_filename,
                "rickshaw_count": max_rickshaw_count,
                "total_entry": total_entry,
                "total_exit": total_exit,
                "net_count": total_entry - total_exit,
                "output_url": output_url,
                "frames_processed": frame_count
            }
            
            job_manager.mark_completed(job_id, result)
            logger.info(f"[Job {job_id}] Marked as completed")
            
        except Exception as e:
            error_msg = f"Error processing video: {str(e)}"
            logger.error(f"[Job {job_id}] {error_msg}", exc_info=True)
            
            # Mark job as failed
            job_manager.mark_failed(job_id, error_msg)
            
            # Clean up temporary files on error
            if temp_input_path.exists():
                temp_input_path.unlink()
            if output_path.exists():
                output_path.unlink()
