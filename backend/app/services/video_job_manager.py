import threading
import time
import cv2
import numpy as np
from typing import Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
from app.core.config import logger


@dataclass
class VideoJobState:
    job_id: str
    status: str  # "processing", "paused", "completed", "failed", "stopped"
    progress: float  # 0.0 to 100.0
    total_frames: int
    processed_frames: int
    latest_frame: Optional[np.ndarray] = None  # Latest processed frame for streaming
    latest_frame_lock: threading.Lock = field(default_factory=threading.Lock)
    error_message: Optional[str] = None
    paused: bool = False
    should_stop: bool = False
    
    # Results (populated when completed)
    output_filename: Optional[str] = None
    output_url: Optional[str] = None
    rickshaw_count: int = 0
    total_entry: int = 0
    total_exit: int = 0
    net_count: int = 0
    
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class VideoJobManager:
    def __init__(self):
        self._jobs: Dict[str, VideoJobState] = {}
        self._jobs_lock = threading.Lock()
        self._cleanup_thread = None
        self._running = True
        
        # Start cleanup thread for old jobs
        self._start_cleanup_thread()
        logger.info("VideoJobManager initialized")
    
    def create_job(self, job_id: str, total_frames: int) -> VideoJobState:
        with self._jobs_lock:
            job_state = VideoJobState(
                job_id=job_id,
                status="processing",
                progress=0.0,
                total_frames=total_frames,
                processed_frames=0
            )
            self._jobs[job_id] = job_state
            logger.info(f"Created job: {job_id} with {total_frames} frames")
            return job_state
    
    def get_job(self, job_id: str) -> Optional[VideoJobState]:
        with self._jobs_lock:
            return self._jobs.get(job_id)
    
    def update_frame(self, job_id: str, frame: np.ndarray, frame_number: int, entry_count: int = 0, exit_count: int = 0):
        job = self.get_job(job_id)
        if job:
            with job.latest_frame_lock:
                job.latest_frame = frame.copy()  # Copy to avoid race conditions
                job.processed_frames = frame_number
                job.total_entry = entry_count
                job.total_exit = exit_count
                
                # Update progress
                if job.total_frames > 0:
                    job.progress = (frame_number / job.total_frames) * 100.0
    
    def get_latest_frame(self, job_id: str) -> Optional[np.ndarray]:
        job = self.get_job(job_id)
        if job and job.latest_frame is not None:
            with job.latest_frame_lock:
                return job.latest_frame.copy()
        return None
    
    def mark_completed(self, job_id: str, result: dict):
        job = self.get_job(job_id)
        if job:
            job.status = "completed"
            job.progress = 100.0
            job.completed_at = datetime.now()
            job.output_filename = result.get("file_name")
            job.output_url = result.get("output_url")
            job.rickshaw_count = result.get("rickshaw_count", 0)
            job.total_entry = result.get("total_entry", 0)
            job.total_exit = result.get("total_exit", 0)
            job.net_count = result.get("net_count", 0)
            logger.info(f"Job completed: {job_id}")
    
    def mark_failed(self, job_id: str, error_message: str):
        job = self.get_job(job_id)
        if job:
            job.status = "failed"
            job.error_message = error_message
            job.completed_at = datetime.now()
            logger.error(f"Job failed: {job_id} - {error_message}")
    
    def pause_job(self, job_id: str) -> bool:
        job = self.get_job(job_id)
        if job and job.status == "processing":
            job.paused = True
            job.status = "paused"
            logger.info(f"Job paused: {job_id}")
            return True
        return False
    
    def resume_job(self, job_id: str) -> bool:
        job = self.get_job(job_id)
        if job and job.status == "paused":
            job.paused = False
            job.status = "processing"
            logger.info(f"Job resumed: {job_id}")
            return True
        return False
    
    def stop_job(self, job_id: str) -> bool:
        job = self.get_job(job_id)
        if job and job.status in ["processing", "paused"]:
            job.should_stop = True
            job.status = "stopped"
            job.completed_at = datetime.now()
            logger.info(f"Job stopped: {job_id}")
            return True
        return False
    
    def delete_job(self, job_id: str):
        with self._jobs_lock:
            if job_id in self._jobs:
                del self._jobs[job_id]
                logger.info(f"Deleted job: {job_id}")
    
    def _start_cleanup_thread(self):
        def cleanup_old_jobs():
            while self._running:
                try:
                    time.sleep(300)  # Run every 5 minutes
                    current_time = datetime.now()
                    
                    with self._jobs_lock:
                        jobs_to_delete = []
                        for job_id, job in self._jobs.items():
                            # Delete completed/failed jobs older than 30 minutes
                            if job.status in ["completed", "failed"] and job.completed_at:
                                age_minutes = (current_time - job.completed_at).total_seconds() / 60
                                if age_minutes > 30:
                                    jobs_to_delete.append(job_id)
                        
                        for job_id in jobs_to_delete:
                            del self._jobs[job_id]
                            logger.info(f"Cleaned up old job: {job_id}")
                
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {str(e)}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_old_jobs, daemon=True)
        self._cleanup_thread.start()
    
    def shutdown(self):
        self._running = False
        logger.info("VideoJobManager shutdown")


# Global job manager instance
_job_manager: Optional[VideoJobManager] = None


def get_job_manager() -> VideoJobManager:
    global _job_manager
    if _job_manager is None:
        _job_manager = VideoJobManager()
    return _job_manager
