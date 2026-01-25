"""
Webcam stream processing service for real-time rickshaw detection.
Optimized with frame skipping and efficient MJPEG streaming.
"""
import cv2
import numpy as np
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Generator
from queue import Queue
from dataclasses import dataclass
from app.model.detector import YOLODetector
from app.utils.draw_utils import draw_detections, draw_entry_exit_line, draw_entry_exit_counts
from app.utils.count_utils import LineCrossingDetector, SimpleTracker
from app.core.config import settings, logger


@dataclass
class WebcamJob:
    """Represents an active webcam streaming job"""
    camera_index: int
    camera_name: str
    status: str  # 'connecting', 'streaming', 'stopped', 'error'
    entry_count: int = 0
    exit_count: int = 0
    net_count: int = 0
    frames_processed: int = 0
    frames_displayed: int = 0
    fps: float = 0.0
    started_at: Optional[datetime] = None
    error_message: Optional[str] = None
    stream_width: int = 0
    stream_height: int = 0
    stream_fps: float = 0.0
    
    # Threading
    thread: Optional[threading.Thread] = None
    stop_event: Optional[threading.Event] = None
    frame_queue: Optional[Queue] = None
    
    # Processing
    tracker: Optional[SimpleTracker] = None
    line_detector: Optional[LineCrossingDetector] = None


class WebcamStreamProcessor:
    """
    Processes webcam streams with real-time YOLOv8 detection.
    Implements frame skipping for performance optimization.
    """
    
    def __init__(
        self,
        detector: YOLODetector,
        camera_index: int = 0,
        frame_skip: int = 3,
        inference_size: tuple = (640, 640),
        camera_name: str = "Webcam"
    ):
        """
        Initialize webcam stream processor.
        
        Args:
            detector: YOLODetector instance
            camera_index: Camera device index (0 for default webcam)
            frame_skip: Process every Nth frame (default: 3)
            inference_size: Size for YOLO inference (width, height)
            camera_name: Display name for camera
        """
        self.detector = detector
        self.camera_index = camera_index
        self.frame_skip = frame_skip
        self.inference_size = inference_size
        self.camera_name = camera_name
        
        # Stream state
        self.cap = None
        self.is_running = False
        self.stop_event = threading.Event()
        
        # Frame queue for MJPEG streaming
        self.frame_queue = Queue(maxsize=10)
        
        # Counting components
        self.tracker = SimpleTracker(max_age=30)
        self.line_detector = None  # Will be initialized with frame dimensions
        
        # Statistics
        self.entry_count = 0
        self.exit_count = 0
        self.net_count = 0
        self.frames_processed = 0
        self.frames_displayed = 0
        self.fps = 0.0
        
        # Stream properties
        self.stream_width = 0
        self.stream_height = 0
        self.stream_fps = 0.0
        
        logger.info(f"WebcamStreamProcessor initialized: camera={camera_index}, frame_skip={frame_skip}")
    
    def start(self) -> Dict:
        """
        Start webcam stream capture and processing.
        
        Returns:
            Dict: Status information
        """
        try:
            # Open webcam
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Cannot open webcam {self.camera_index}")
            
            # Get stream properties
            self.stream_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.stream_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.stream_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Webcam opened: {self.stream_width}x{self.stream_height} @ {self.stream_fps}fps")
            
            # Initialize line detector with frame dimensions
            line_y = int(self.stream_height * 0.5)  # Middle of frame
            self.line_detector = LineCrossingDetector(line_y=line_y)
            
            # Start processing
            self.is_running = True
            self.stop_event.clear()
            
            return {
                "success": True,
                "message": "Webcam stream started",
                "width": self.stream_width,
                "height": self.stream_height,
                "fps": self.stream_fps
            }
            
        except Exception as e:
            logger.error(f"Failed to start webcam: {str(e)}")
            if self.cap:
                self.cap.release()
            raise RuntimeError(f"Failed to start webcam: {str(e)}")
    
    def process_frames(self) -> Generator[bytes, None, None]:
        """
        Main processing loop. Yields MJPEG frames.
        Implements frame skipping for performance.
        
        Yields:
            bytes: JPEG-encoded frame
        """
        frame_counter = 0
        fps_counter = 0
        fps_start_time = time.time()
        last_detections = []
        last_track_ids = {}
        
        try:
            while self.is_running and not self.stop_event.is_set():
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame from webcam")
                    break
                
                frame_counter += 1
                self.frames_displayed += 1
                
                # Perform detection only on skipped frames
                if frame_counter % self.frame_skip == 0:
                    self.frames_processed += 1
                    
                    # Resize frame for inference (optimization)
                    inference_frame = cv2.resize(frame, self.inference_size)
                    
                    # Run YOLO detection
                    detections = self.detector.detect(inference_frame)
                    
                    # Scale bounding boxes back to original frame size
                    scale_x = self.stream_width / self.inference_size[0]
                    scale_y = self.stream_height / self.inference_size[1]
                    
                    for det in detections:
                        det['bbox'] = [
                            int(det['bbox'][0] * scale_x),
                            int(det['bbox'][1] * scale_y),
                            int(det['bbox'][2] * scale_x),
                            int(det['bbox'][3] * scale_y)
                        ]
                    
                    # Update tracker
                    tracked_objects = self.tracker.update(detections)
                    
                    # Check line crossings
                    for obj in tracked_objects:
                        track_id = obj['track_id']
                        bbox = obj['bbox']
                        center_y = (bbox[1] + bbox[3]) // 2
                        
                        crossing = self.line_detector.check_crossing(track_id, center_y)
                        
                        if crossing == 'entry':
                            self.entry_count += 1
                            self.net_count += 1
                            logger.info(f"Entry detected: ID={track_id}, Entry={self.entry_count}")
                        elif crossing == 'exit':
                            self.exit_count += 1
                            self.net_count -= 1
                            logger.info(f"Exit detected: ID={track_id}, Exit={self.exit_count}")
                    
                    last_detections = tracked_objects
                    last_track_ids = {obj['track_id']: obj for obj in tracked_objects}
                
                # Draw on every frame (using last detections)
                annotated_frame = frame.copy()
                
                # Draw entry/exit line
                draw_entry_exit_line(annotated_frame, self.line_detector.line_y)
                
                # Draw detections with track IDs
                if last_detections:
                    draw_detections(annotated_frame, last_detections)
                
                # Draw counts
                draw_entry_exit_counts(
                    annotated_frame,
                    self.entry_count,
                    self.exit_count,
                    self.net_count
                )
                
                # Add FPS and frame info
                cv2.putText(
                    annotated_frame,
                    f"FPS: {self.fps:.1f} | Processed: {self.frames_processed}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                
                # Calculate FPS
                fps_counter += 1
                if fps_counter >= 30:
                    elapsed = time.time() - fps_start_time
                    self.fps = fps_counter / elapsed if elapsed > 0 else 0.0
                    fps_counter = 0
                    fps_start_time = time.time()
                
                # Encode frame to JPEG
                _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()
                
                # Yield frame in MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                # Small delay to prevent overwhelming the CPU
                time.sleep(0.01)
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop webcam stream and release resources"""
        logger.info("Stopping webcam stream...")
        self.is_running = False
        self.stop_event.set()
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        logger.info("Webcam stream stopped")
    
    def get_status(self) -> Dict:
        """Get current stream status and statistics"""
        return {
            "camera_index": self.camera_index,
            "camera_name": self.camera_name,
            "status": "streaming" if self.is_running else "stopped",
            "entry_count": self.entry_count,
            "exit_count": self.exit_count,
            "net_count": self.net_count,
            "frames_processed": self.frames_processed,
            "frames_displayed": self.frames_displayed,
            "fps": round(self.fps, 2),
            "stream_properties": {
                "width": self.stream_width,
                "height": self.stream_height,
                "fps": self.stream_fps
            } if self.stream_width > 0 else None,
            "config": {
                "frame_skip": self.frame_skip,
                "inference_size": self.inference_size
            }
        }


class WebcamService:
    """
    Singleton service to manage webcam streaming jobs.
    """
    
    def __init__(self):
        self.active_streams: Dict[str, WebcamStreamProcessor] = {}
        self.detector = None
        logger.info("WebcamService initialized")
    
    def _get_detector(self) -> YOLODetector:
        """Get or create YOLODetector instance (singleton)"""
        if self.detector is None:
            self.detector = YOLODetector()
        return self.detector
    
    def start_stream(
        self,
        camera_index: int = 0,
        camera_name: str = "Webcam",
        frame_skip: int = 3
    ) -> Dict:
        """
        Start a webcam stream.
        
        Args:
            camera_index: Camera device index (0 for default)
            camera_name: Display name
            frame_skip: Process every Nth frame
            
        Returns:
            Dict: Status information
        """
        stream_id = f"webcam_{camera_index}"
        
        # Stop existing stream if any
        if stream_id in self.active_streams:
            self.stop_stream(camera_index)
        
        try:
            detector = self._get_detector()
            processor = WebcamStreamProcessor(
                detector=detector,
                camera_index=camera_index,
                frame_skip=frame_skip,
                camera_name=camera_name
            )
            
            result = processor.start()
            self.active_streams[stream_id] = processor
            
            logger.info(f"Webcam stream started: {stream_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to start webcam stream: {str(e)}")
            raise
    
    def stop_stream(self, camera_index: int = 0) -> Dict:
        """Stop a webcam stream"""
        stream_id = f"webcam_{camera_index}"
        
        if stream_id in self.active_streams:
            processor = self.active_streams[stream_id]
            processor.stop()
            del self.active_streams[stream_id]
            logger.info(f"Webcam stream stopped: {stream_id}")
            return {"success": True, "message": "Stream stopped"}
        
        return {"success": False, "message": "Stream not found"}
    
    def get_stream_processor(self, camera_index: int = 0) -> Optional[WebcamStreamProcessor]:
        """Get active stream processor"""
        stream_id = f"webcam_{camera_index}"
        return self.active_streams.get(stream_id)
    
    def get_status(self, camera_index: int = 0) -> Dict:
        """Get stream status"""
        processor = self.get_stream_processor(camera_index)
        if processor:
            return processor.get_status()
        
        return {
            "camera_index": camera_index,
            "status": "stopped",
            "message": "No active stream"
        }
    
    def list_streams(self) -> Dict:
        """List all active streams"""
        streams = []
        for stream_id, processor in self.active_streams.items():
            streams.append(processor.get_status())
        
        return {
            "success": True,
            "count": len(streams),
            "streams": streams
        }


# Singleton instance
_webcam_service = None

def get_webcam_service() -> WebcamService:
    """Get singleton WebcamService instance"""
    global _webcam_service
    if _webcam_service is None:
        _webcam_service = WebcamService()
    return _webcam_service
