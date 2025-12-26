"""
CCTV/RTSP stream processing service.
Handles real-time detection from camera streams with entry/exit counting.
"""
import cv2
import numpy as np
import json
import time
import threading
from typing import Optional, Dict
from app.model.detector import YOLODetector
from app.utils.draw_utils import (
    draw_detections, draw_entry_exit_line, draw_entry_exit_counts
)
from app.utils.count_utils import LineCrossingDetector, SimpleTracker
from app.db.database import log_rickshaw_event
from app.core.config import settings, logger


class CCTVStreamProcessor:
    """
    Processes RTSP/CCTV streams for real-time rickshaw detection.
    Handles stream connection, reconnection, and entry/exit counting.
    """
    
    def __init__(
        self,
        detector: YOLODetector,
        camera_id: str,
        rtsp_url: str,
        camera_name: str = "Camera"
    ):
        """
        Initialize CCTV stream processor.
        
        Args:
            detector: YOLODetector instance
            camera_id: Unique camera identifier
            rtsp_url: RTSP stream URL
            camera_name: Human-readable camera name
        """
        self.detector = detector
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.camera_name = camera_name
        
        self.is_running = False
        self.cap: Optional[cv2.VideoCapture] = None
        self.line_detector: Optional[LineCrossingDetector] = None
        self.tracker: Optional[SimpleTracker] = None
        
        self.frame_count = 0
        self.frames_processed = 0
        self.entry_count = 0
        self.exit_count = 0
        
        logger.info(f"CCTVStreamProcessor initialized for camera: {camera_id} ({camera_name})")
    
    def connect(self) -> bool:
        """
        Connect to RTSP stream.
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"Connecting to stream: {self.rtsp_url}")
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open stream: {self.rtsp_url}")
                return False
            
            # Get stream properties
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            logger.info(f"Stream connected: {width}x{height} @ {fps}fps")
            
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
            return False
    
    def disconnect(self):
        """Disconnect from stream and cleanup resources."""
        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info(f"Stream disconnected: {self.camera_id}")
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to stream.
        
        Returns:
            bool: True if reconnection successful
        """
        logger.info(f"Attempting to reconnect camera: {self.camera_id}")
        self.disconnect()
        
        for attempt in range(settings.stream_reconnect_attempts):
            logger.info(f"Reconnection attempt {attempt + 1}/{settings.stream_reconnect_attempts}")
            
            if self.connect():
                logger.info(f"Reconnection successful")
                return True
            
            time.sleep(settings.stream_reconnect_delay)
        
        logger.error(f"Reconnection failed after {settings.stream_reconnect_attempts} attempts")
        return False
    
    def process_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Process a single frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Optional[np.ndarray]: Annotated frame or None if processing failed
        """
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
            return annotated_frame
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return None
    
    def process_stream(self, duration: Optional[int] = None) -> Dict:
        """
        Process stream for a specified duration.
        
        Args:
            duration: Duration in seconds (None for continuous)
            
        Returns:
            Dict: Processing statistics
        """
        if not self.connect():
            raise RuntimeError(f"Failed to connect to stream: {self.rtsp_url}")
        
        self.is_running = True
        start_time = time.time()
        last_frame_time = start_time
        
        logger.info(f"Starting stream processing: camera={self.camera_id}, duration={duration}s")
        
        try:
            while self.is_running:
                # Check duration limit
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
        """Stop stream processing."""
        self.is_running = False
        logger.info(f"Stop requested for camera: {self.camera_id}")


class CCTVService:
    """
    Service for managing multiple CCTV streams.
    """
    
    def __init__(self, detector: YOLODetector):
        """
        Initialize CCTV service.
        
        Args:
            detector: YOLODetector instance
        """
        self.detector = detector
        self.active_streams: Dict[str, CCTVStreamProcessor] = {}
        logger.info("CCTVService initialized")
    
    async def start_stream(
        self,
        camera_id: str,
        rtsp_url: str,
        duration: Optional[int] = None,
        camera_name: str = "Camera"
    ) -> Dict:
        """
        Start processing a CCTV stream.
        
        Args:
            camera_id: Unique camera identifier
            rtsp_url: RTSP stream URL
            duration: Duration to process in seconds (None for continuous)
            camera_name: Human-readable camera name
            
        Returns:
            Dict: Processing statistics
        """
        # Check concurrent stream limit
        if len(self.active_streams) >= settings.max_concurrent_streams:
            raise RuntimeError(
                f"Maximum concurrent streams ({settings.max_concurrent_streams}) reached"
            )
        
        # Create stream processor
        processor = CCTVStreamProcessor(
            detector=self.detector,
            camera_id=camera_id,
            rtsp_url=rtsp_url,
            camera_name=camera_name
        )
        
        self.active_streams[camera_id] = processor
        
        try:
            # Process stream (blocking call)
            stats = processor.process_stream(duration=duration)
            return stats
            
        finally:
            # Remove from active streams
            if camera_id in self.active_streams:
                del self.active_streams[camera_id]
    
    def stop_stream(self, camera_id: str):
        """
        Stop a specific stream.
        
        Args:
            camera_id: Camera identifier
        """
        if camera_id in self.active_streams:
            self.active_streams[camera_id].stop()
            logger.info(f"Stop signal sent to camera: {camera_id}")
        else:
            logger.warning(f"Camera not found in active streams: {camera_id}")
    
    def stop_all_streams(self):
        """Stop all active streams."""
        for camera_id in list(self.active_streams.keys()):
            self.stop_stream(camera_id)
        logger.info("All streams stopped")
    
    def get_active_streams(self) -> list:
        """
        Get list of active streams.
        
        Returns:
            list: List of active camera IDs
        """
        return list(self.active_streams.keys())
