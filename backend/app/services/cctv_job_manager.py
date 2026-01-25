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
    def __init__(self):
        self._jobs: Dict[str, CCTVJobState] = {}
        self._jobs_lock = threading.Lock()
        logger.info("CCTVJobManager initialized")
    
    def create_job(
        self,
        camera_id: str,
        rtsp_url: str,
        camera_name: str = "Camera"
    ) -> CCTVJobState:
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
        with self._jobs_lock:
            return self._jobs.get(camera_id)
    
    def update_status(self, camera_id: str, status: str, error_message: Optional[str] = None):
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
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].stream_width = width
                self._jobs[camera_id].stream_height = height
                self._jobs[camera_id].stream_fps = fps
                logger.info(f"Camera {camera_id} properties: {width}x{height} @ {fps}fps")
    
    def set_started(self, camera_id: str):
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].started_at = datetime.now()
                self._jobs[camera_id].status = "streaming"
    
    def stop_job(self, camera_id: str):
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].status = "stopped"
                logger.info(f"Stopped camera: {camera_id}")
    
    def remove_job(self, camera_id: str):
        with self._jobs_lock:
            if camera_id in self._jobs:
                del self._jobs[camera_id]
                logger.info(f"Removed camera job: {camera_id}")
    
    def get_all_jobs(self) -> Dict[str, CCTVJobState]:
        with self._jobs_lock:
            return dict(self._jobs)
    
    def increment_reconnect_attempts(self, camera_id: str) -> int:
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].reconnect_attempts += 1
                return self._jobs[camera_id].reconnect_attempts
        return 0
    
    def reset_reconnect_attempts(self, camera_id: str):
        with self._jobs_lock:
            if camera_id in self._jobs:
                self._jobs[camera_id].reconnect_attempts = 0


# Singleton instance
_cctv_job_manager: Optional[CCTVJobManager] = None
_manager_lock = threading.Lock()


def get_cctv_job_manager() -> CCTVJobManager:
    global _cctv_job_manager
    
    if _cctv_job_manager is None:
        with _manager_lock:
            if _cctv_job_manager is None:
                _cctv_job_manager = CCTVJobManager()
    
    return _cctv_job_manager
