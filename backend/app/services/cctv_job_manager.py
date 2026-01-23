"""
CCTV job manager for handling live RTSP stream processing with real-time preview.
Manages continuous camera stream states in memory for live MJPEG streaming.
"""
import threading
import time
import cv2
import numpy as np
from typing import Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
from app.core.config import logger


@dataclass
class CCTVJobState:
    """Represents the state of a live CCTV stream processing job."""
    camera_id: str
    status: str  # "idle", "connecting", "streaming", "stopped", "error"
    rtsp_url: str
    camera_name: str
    
    # Live streaming data
    latest_frame: Optional[np.ndarray] = None  # Latest processed frame for MJPEG streaming
    latest_frame_lock: threading.Lock = field(default_factory=threading.Lock)
    
    # Live statistics (updated continuously)
    entry_count: int = 0
    exit_count: int = 0
    net_count: int = 0
    frames_processed: int = 0
    
    # Performance metrics
    fps: float = 0.0
    started_at: Optional[datetime] = None
    last_frame_time: Optional[datetime] = None
    
    # Error handling
    error_message: Optional[str] = None
    reconnect_attempts: int = 0
    
    # Stream properties (populated after connection)
    stream_width: int = 0
    stream_height: int = 0
    stream_fps: int = 0


class CCTVJobManager:
    """
    Manages live CCTV stream processing jobs in memory.
    Provides thread-safe access to camera states for live streaming.
    """
    
    def __init__(self):
        """Initialize the CCTV job manager."""
        self._jobs: Dict[str, CCTVJobState] = {}
        self._jobs_lock = threading.Lock()
        logger.info("CCTVJobManager initialized")
    
    def create_job(
        self,
        camera_id: str,
        rtsp_url: str,
        camera_name: str = "Camera"
    ) -> CCTVJobState:
        """
        Create a new CCTV streaming job.
        
        Args:
            camera_id: Unique camera identifier
            rtsp_url: RTSP stream URL
            camera_name: Human-readable camera name
            
        Returns:
            CCTVJobState: Created job state
        """
        with self._jobs_lock:
            # Check if camera already exists
            if camera_id in self._jobs:
                existing_job = self._jobs[camera_id]
                if existing_job.status == "streaming":
                    logger.warning(f"Camera {camera_id} is already streaming")
                    return existing_job
            
            job_state = CCTVJobState(
                camera_id=camera_id,
                status="idle",
                rtsp_url=rtsp_url,
                camera_name=camera_name
            )
            self._jobs[camera_id] = job_state
            logger.info(f"Created CCTV job: {camera_id} ({camera_name})")
            return job_state
    
    def get_job(self, camera_id: str) -> Optional[CCTVJobState]:
        """
        Get CCTV job state by camera ID.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            CCTVJobState or None if not found
        """
        with self._jobs_lock:
            return self._jobs.get(camera_id)
    
    def update_status(self, camera_id: str, status: str, error_message: Optional[str] = None):
        """
        Update the status of a CCTV job.
        
        Args:
            camera_id: Camera identifier
            status: New status ("connecting", "streaming", "stopped", "error")
            error_message: Optional error message
        """
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].status = status
                if error_message:
                    self._jobs[camera_id].error_message = error_message
                logger.info(f"Camera {camera_id} status: {status}")
    
    def update_frame(
        self,
        camera_id: str,
        frame: np.ndarray,
        entry_count: int,
        exit_count: int
    ):
        """
        Update the latest processed frame and counts for a camera.
        Thread-safe method to update the frame that will be streamed via MJPEG.
        
        Args:
            camera_id: Camera identifier
            frame: Processed frame with annotations (numpy array)
            entry_count: Current entry count
            exit_count: Current exit count
        """
        job = self.get_job(camera_id)
        if not job:
            return
        
        # Update frame with lock
        with job.latest_frame_lock:
            job.latest_frame = frame.copy()
            job.entry_count = entry_count
            job.exit_count = exit_count
            job.net_count = entry_count - exit_count
            job.frames_processed += 1
            job.last_frame_time = datetime.now()
            
            # Calculate FPS
            if job.started_at:
                elapsed = (datetime.now() - job.started_at).total_seconds()
                if elapsed > 0:
                    job.fps = job.frames_processed / elapsed
    
    def get_latest_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """
        Get the latest processed frame for a camera.
        Thread-safe method to retrieve frame for MJPEG streaming.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Latest frame as numpy array or None
        """
        job = self.get_job(camera_id)
        if not job:
            return None
        
        with job.latest_frame_lock:
            if job.latest_frame is not None:
                return job.latest_frame.copy()
        return None
    
    def update_stream_properties(
        self,
        camera_id: str,
        width: int,
        height: int,
        fps: int
    ):
        """
        Update stream properties after successful connection.
        
        Args:
            camera_id: Camera identifier
            width: Stream width in pixels
            height: Stream height in pixels
            fps: Stream FPS
        """
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].stream_width = width
                self._jobs[camera_id].stream_height = height
                self._jobs[camera_id].stream_fps = fps
                logger.info(f"Camera {camera_id} properties: {width}x{height} @ {fps}fps")
    
    def set_started(self, camera_id: str):
        """
        Mark camera as started streaming.
        
        Args:
            camera_id: Camera identifier
        """
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].started_at = datetime.now()
                self._jobs[camera_id].status = "streaming"
    
    def stop_job(self, camera_id: str):
        """
        Stop a CCTV streaming job.
        
        Args:
            camera_id: Camera identifier
        """
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].status = "stopped"
                logger.info(f"Stopped camera: {camera_id}")
    
    def remove_job(self, camera_id: str):
        """
        Remove a CCTV job from manager.
        
        Args:
            camera_id: Camera identifier
        """
        with self._jobs_lock:
            if camera_id in self._jobs:
                del self._jobs[camera_id]
                logger.info(f"Removed camera job: {camera_id}")
    
    def get_all_jobs(self) -> Dict[str, CCTVJobState]:
        """
        Get all CCTV jobs.
        
        Returns:
            Dictionary of camera_id -> CCTVJobState
        """
        with self._jobs_lock:
            return dict(self._jobs)
    
    def increment_reconnect_attempts(self, camera_id: str) -> int:
        """
        Increment reconnection attempts counter.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Current attempt count
        """
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].reconnect_attempts += 1
                return self._jobs[camera_id].reconnect_attempts
        return 0
    
    def reset_reconnect_attempts(self, camera_id: str):
        """
        Reset reconnection attempts counter after successful connection.
        
        Args:
            camera_id: Camera identifier
        """
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].reconnect_attempts = 0


# Singleton instance
_cctv_job_manager: Optional[CCTVJobManager] = None
_manager_lock = threading.Lock()


def get_cctv_job_manager() -> CCTVJobManager:
    """
    Get the singleton CCTVJobManager instance.
    Thread-safe lazy initialization.
    
    Returns:
        CCTVJobManager: The singleton manager instance
    """
    global _cctv_job_manager
    
    if _cctv_job_manager is None:
        with _manager_lock:
            if _cctv_job_manager is None:
                _cctv_job_manager = CCTVJobManager()
    
    return _cctv_job_manager
