import cv2
import numpy as np
import json
import time
import threading
from datetime import datetime
from typing import Optional, Dict
from app.model.detector import YOLODetector
from app.utils.draw_utils import (
    draw_detections, draw_entry_exit_line, draw_entry_exit_counts
)
from app.utils.count_utils import LineCrossingDetector, SimpleTracker
from app.db.database import log_rickshaw_event
from app.services.cctv_job_manager import get_cctv_job_manager
from app.core.config import settings, logger


class CCTVStreamProcessor:
    def __init__(
        self,
        detector: YOLODetector,
        camera_id: str,
        rtsp_url: str,
        camera_name: str = "Camera",
        continuous_mode: bool = False  # NEW: Enable continuous streaming mode
    ):
        self.detector = detector
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.camera_name = camera_name
        self.continuous_mode = continuous_mode  # NEW: Streaming mode flag
        
        self.is_running = False
        self.cap: Optional[cv2.VideoCapture] = None
        self.line_detector: Optional[LineCrossingDetector] = None
        self.tracker: Optional[SimpleTracker] = None
        
        self.frame_count = 0
        self.frames_processed = 0
        self.entry_count = 0
        self.exit_count = 0
        
        # NEW: Job manager for live streaming
        self.job_manager = get_cctv_job_manager() if continuous_mode else None
        
        logger.info(f"CCTVStreamProcessor initialized for camera: {camera_id} ({camera_name}), "
                   f"continuous_mode={continuous_mode}")
    
    def connect(self) -> bool:
        try:
            logger.info(f"Connecting to stream: {self.rtsp_url}")
            
            # NEW: Update status to connecting if in continuous mode
            if self.continuous_mode and self.job_manager:
                self.job_manager.update_status(self.camera_id, "connecting")
            
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open stream: {self.rtsp_url}")
                
                # NEW: Update status to error if in continuous mode
                if self.continuous_mode and self.job_manager:
                    self.job_manager.update_status(
                        self.camera_id, "error",
                        f"Failed to open stream: {self.rtsp_url}"
                    )
                return False
            
            # Get stream properties
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            logger.info(f"Stream connected: {width}x{height} @ {fps}fps")
            
            # NEW: Update stream properties if in continuous mode
            if self.continuous_mode and self.job_manager:
                self.job_manager.update_stream_properties(self.camera_id, width, height, fps)
            
            # Initialize line crossing detector
            self.line_detector = LineCrossingDetector(
                line_start=settings.entry_line_start,
                line_end=settings.entry_line_end,
                frame_width=width,
                frame_height=height,
                use_percentage=True
            )
            
            # Initialize tracker
            self.tracker = SimpleTracker()
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to stream: {str(e)}", exc_info=True)
            
            # NEW: Update status to error if in continuous mode
            if self.continuous_mode and self.job_manager:
                self.job_manager.update_status(
                    self.camera_id, "error",
                    f"Connection error: {str(e)}"
                )
            return False
    
    def disconnect(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info(f"Stream disconnected: {self.camera_id}")
    
    def reconnect(self) -> bool:
        logger.info(f"Attempting to reconnect camera: {self.camera_id}")
        self.disconnect()
        
        # NEW: Track reconnection attempts in continuous mode
        if self.continuous_mode and self.job_manager:
            attempts = self.job_manager.increment_reconnect_attempts(self.camera_id)
            logger.info(f"Reconnection attempt {attempts}/{settings.stream_reconnect_attempts}")
        
        for attempt in range(settings.stream_reconnect_attempts):
            logger.info(f"Reconnection attempt {attempt + 1}/{settings.stream_reconnect_attempts}")
            
            if self.connect():
                logger.info(f"Reconnection successful")
                
                # NEW: Reset reconnection attempts in continuous mode
                if self.continuous_mode and self.job_manager:
                    self.job_manager.reset_reconnect_attempts(self.camera_id)
                return True
            
            time.sleep(settings.stream_reconnect_delay)
        
        logger.error(f"Reconnection failed after {settings.stream_reconnect_attempts} attempts")
        
        # NEW: Update status to error in continuous mode
        if self.continuous_mode and self.job_manager:
            self.job_manager.update_status(
                self.camera_id, "error",
                f"Reconnection failed after {settings.stream_reconnect_attempts} attempts"
            )
        return False
    
    def process_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        try:
            # Run detection
            detection_result = self.detector.detect(frame)
            
            # Draw detections
            annotated_frame = draw_detections(frame, detection_result, self.detector)
            
            # Track objects and check for line crossings
            if len(detection_result) > 0 and self.line_detector and self.tracker:
                # Update tracker
                tracked_objects = self.tracker.update(detection_result.boxes)
                
                # Check each tracked object for line crossing
                for track_id, bbox in tracked_objects.items():
                    event = self.line_detector.update(
                        object_id=str(track_id),
                        bbox=bbox,
                        frame_number=self.frame_count
                    )
                    
                    # Log event to database
                    if event:
                        bbox_json = json.dumps(bbox.tolist())
                        confidence = detection_result.confidences[0] if len(detection_result.confidences) > 0 else 0.0
                        
                        log_rickshaw_event(
                            event_type=event,
                            confidence=float(confidence),
                            camera_id=self.camera_id,
                            rickshaw_id=str(track_id),
                            frame_number=self.frame_count,
                            bounding_box=bbox_json,
                            crossing_line="entry_line",
                            notes=f"Camera: {self.camera_name}"
                        )
                        
                        if event == "entry":
                            self.entry_count += 1
                        elif event == "exit":
                            self.exit_count += 1
                
                # Draw line and counts
                if self.line_detector:
                    line_start, line_end = self.line_detector.get_line_pixels()
                    annotated_frame = draw_entry_exit_line(
                        annotated_frame, line_start, line_end, 
                        label=f"{self.camera_name}"
                    )
                    
                    entry, exit_count, net = self.line_detector.get_counts()
                    annotated_frame = draw_entry_exit_counts(
                        annotated_frame, entry, exit_count, net
                    )
            
            self.frames_processed += 1
            
            # NEW: Update job manager with latest frame in continuous mode
            if self.continuous_mode and self.job_manager:
                self.job_manager.update_frame(
                    self.camera_id,
                    annotated_frame,
                    self.entry_count,
                    self.exit_count
                )
            
            return annotated_frame
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return None
    
    def process_stream(self, duration: Optional[int] = None) -> Dict:
        if not self.connect():
            raise RuntimeError(f"Failed to connect to stream: {self.rtsp_url}")
        
        self.is_running = True
        start_time = time.time()
        last_frame_time = start_time
        
        # NEW: Mark as started in continuous mode
        if self.continuous_mode and self.job_manager:
            self.job_manager.set_started(self.camera_id)
        
        # Determine processing mode
        if self.continuous_mode:
            logger.info(f"Starting continuous stream processing: camera={self.camera_id}")
        else:
            logger.info(f"Starting batch stream processing: camera={self.camera_id}, duration={duration}s")
        
        try:
            while self.is_running:
                # NEW: Check if stopped in continuous mode
                if self.continuous_mode and self.job_manager:
                    job = self.job_manager.get_job(self.camera_id)
                    if job and job.status == "stopped":
                        logger.info(f"Stream stopped by user: {self.camera_id}")
                        break
                
                # Check duration limit (only for batch mode)
                if duration and (time.time() - start_time) >= duration:
                    logger.info(f"Duration limit reached: {duration}s")
                    break
                
                # Read frame
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame, attempting reconnection...")
                    if not self.reconnect():
                        break
                    continue
                
                self.frame_count += 1
                
                # Apply FPS limit
                current_time = time.time()
                elapsed = current_time - last_frame_time
                min_frame_time = 1.0 / settings.stream_fps_limit
                
                if elapsed < min_frame_time:
                    time.sleep(min_frame_time - elapsed)
                
                last_frame_time = time.time()
                
                # Process frame
                annotated_frame = self.process_frame(frame)
                
                # Log progress periodically
                if self.frames_processed % 100 == 0:
                    logger.info(f"Processed {self.frames_processed} frames, "
                              f"Entry: {self.entry_count}, Exit: {self.exit_count}")
        
        finally:
            self.is_running = False
            
            # NEW: Update status to stopped in continuous mode
            if self.continuous_mode and self.job_manager:
                self.job_manager.update_status(self.camera_id, "stopped")
            
            self.disconnect()
        
        processing_time = time.time() - start_time
        
        stats = {
            "camera_id": self.camera_id,
            "camera_name": self.camera_name,
            "total_entry": self.entry_count,
            "total_exit": self.exit_count,
            "net_count": self.entry_count - self.exit_count,
            "frames_processed": self.frames_processed,
            "duration": processing_time,
            "avg_fps": self.frames_processed / processing_time if processing_time > 0 else 0
        }
        
        logger.info(f"Stream processing complete: {stats}")
        return stats
    
    def stop(self):
        self.is_running = False
        logger.info(f"Stop requested for camera: {self.camera_id}")


class CCTVService:
    def __init__(self, detector: YOLODetector):
        self.detector = detector
        self.active_streams: Dict[str, CCTVStreamProcessor] = {}
        self.active_threads: Dict[str, threading.Thread] = {}  # NEW: Track processing threads
        self.job_manager = get_cctv_job_manager()  # NEW: Job manager for continuous mode
        logger.info("CCTVService initialized")
    

    def start_continuous_stream(
        self,
        camera_id: str,
        rtsp_url: str,
        camera_name: str = "Camera"
    ) -> Dict:
        # Check if camera already streaming
        if camera_id in self.active_streams:
            existing_processor = self.active_streams[camera_id]
            if existing_processor.is_running:
                logger.warning(f"Camera {camera_id} is already streaming")
                raise RuntimeError(f"Camera {camera_id} is already streaming")
        
        # Check concurrent stream limit
        if len(self.active_streams) >= settings.max_concurrent_streams:
            raise RuntimeError(
                f"Maximum concurrent streams ({settings.max_concurrent_streams}) reached"
            )
        
        # Create job in job manager
        self.job_manager.create_job(camera_id, rtsp_url, camera_name)
        
        # Create stream processor in continuous mode
        processor = CCTVStreamProcessor(
            detector=self.detector,
            camera_id=camera_id,
            rtsp_url=rtsp_url,
            camera_name=camera_name,
            continuous_mode=True  # Enable continuous streaming
        )
        
        self.active_streams[camera_id] = processor
        
        # Start processing in background thread
        def process_continuous():
            try:
                processor.process_stream(duration=None)  # No duration limit
            except Exception as e:
                logger.error(f"Error in continuous stream processing: {str(e)}", exc_info=True)
                self.job_manager.update_status(camera_id, "error", str(e))
            finally:
                # Cleanup after stopped
                if camera_id in self.active_streams:
                    del self.active_streams[camera_id]
                if camera_id in self.active_threads:
                    del self.active_threads[camera_id]
        
        thread = threading.Thread(target=process_continuous, daemon=True)
        thread.start()
        self.active_threads[camera_id] = thread
        
        logger.info(f"Started continuous stream: {camera_id}")
        
        return {
            "success": True,
            "camera_id": camera_id,
            "camera_name": camera_name,
            "status": "connecting",
            "message": f"Camera {camera_id} started, connecting to stream..."
        }
    
    def stop_continuous_stream(self, camera_id: str) -> Dict:
        # Check if camera exists
        job = self.job_manager.get_job(camera_id)
        if not job:
            raise RuntimeError(f"Camera {camera_id} not found")
        
        # Signal processor to stop
        if camera_id in self.active_streams:
            processor = self.active_streams[camera_id]
            processor.stop()
        
        # Update job manager
        self.job_manager.stop_job(camera_id)
        
        logger.info(f"Stopped continuous stream: {camera_id}")
        
        return {
            "success": True,
            "camera_id": camera_id,
            "message": f"Camera {camera_id} stopped successfully"
        }
    
    def get_stream_status(self, camera_id: str) -> Dict:
        job = self.job_manager.get_job(camera_id)
        
        if not job:
            raise RuntimeError(f"Camera {camera_id} not found")
        
        # Calculate uptime
        uptime = 0.0
        if job.started_at:
            uptime = (datetime.now() - job.started_at).total_seconds()
        
        return {
            "success": True,
            "camera_id": camera_id,
            "camera_name": job.camera_name,
            "status": job.status,
            "entry_count": job.entry_count,
            "exit_count": job.exit_count,
            "net_count": job.net_count,
            "frames_processed": job.frames_processed,
            "fps": round(job.fps, 2),
            "uptime": round(uptime, 2),
            "stream_properties": {
                "width": job.stream_width,
                "height": job.stream_height,
                "fps": job.stream_fps
            } if job.stream_width > 0 else None,
            "error_message": job.error_message
        }
    
    def list_active_streams(self) -> Dict:
        all_jobs = self.job_manager.get_all_jobs()
        
        streams = []
        for camera_id, job in all_jobs.items():
            streams.append({
                "camera_id": camera_id,
                "camera_name": job.camera_name,
                "status": job.status,
                "entry_count": job.entry_count,
                "exit_count": job.exit_count,
                "net_count": job.net_count,
                "fps": round(job.fps, 2)
            })
        
        return {
            "success": True,
            "total_streams": len(streams),
            "streams": streams
        }
    
    def stop_all_streams(self):
        for camera_id in list(self.active_streams.keys()):
            self.stop_continuous_stream(camera_id)
        logger.info("All streams stopped")
    
    def get_active_streams(self) -> list:
        return list(self.active_streams.keys())
