"""
Configuration module for the FastAPI application.
Contains all application settings and environment configurations.
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Tuple
import logging


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application Info
    app_name: str = "Smart Rickshaw Entry-Exit Monitoring System"
    version: str = "2.0.0"
    description: str = "FastAPI backend for rickshaw detection with entry-exit monitoring using YOLO"
    
    # API Settings
    api_prefix: str = "/api"
    debug: bool = True
    
    # CORS Settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    # File Upload Settings
    max_upload_size: int = 500 * 1024 * 1024  # 500 MB
    allowed_image_extensions: set = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    allowed_video_extensions: set = {".mp4", ".avi", ".mov", ".mkv"}
    
    # Path Settings
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    model_path: Path = base_dir / "app" / "model" / "best.pt"
    outputs_dir: Path = base_dir / "outputs"
    images_output_dir: Path = outputs_dir / "images"
    videos_output_dir: Path = outputs_dir / "videos"
    database_path: Path = base_dir / "database" / "detections.db"
    logs_dir: Path = base_dir / "logs"
    
    # YOLO Settings
    yolo_confidence: float = 0.25
    yolo_iou: float = 0.45
    yolo_device: str = "cpu"  # Change to "cuda" if GPU is available
    
    # Detection Settings
    target_class: str = "rickshaw"  # Class name to detect
    
    # Entry-Exit Line Settings
    # Line is defined as two points: (x1, y1) to (x2, y2)
    # Coordinates are in percentage (0-100) of frame width/height
    entry_line_start: Tuple[float, float] = (30.0, 50.0)  # (x%, y%)
    entry_line_end: Tuple[float, float] = (70.0, 50.0)    # (x%, y%)
    
    # Alternative: Define separate entry and exit lines
    use_separate_lines: bool = False
    exit_line_start: Tuple[float, float] = (30.0, 60.0)
    exit_line_end: Tuple[float, float] = (70.0, 60.0)
    
    # Counting Settings
    crossing_threshold: int = 5  # Pixels to consider a crossing
    min_detection_confidence: float = 0.3  # Minimum confidence for counting
    track_history_length: int = 30  # Number of frames to keep in tracking history
    
    # CCTV / RTSP Settings
    max_concurrent_streams: int = 4  # Maximum number of simultaneous streams
    stream_reconnect_attempts: int = 3
    stream_reconnect_delay: int = 5  # seconds
    stream_fps_limit: int = 15  # Process max 15 FPS from stream
    
    # Camera Configuration (for multiple cameras)
    cameras: dict = {
        "camera_1": {
            "name": "Main Gate",
            "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
            "enabled": False
        },
        "camera_2": {
            "name": "Side Entrance",
            "rtsp_url": "rtsp://admin:password@192.168.1.101:554/stream1",
            "enabled": False
        }
    }
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "rickshaw_detection.log"
    log_max_bytes: int = 10485760  # 10 MB
    log_backup_count: int = 5  # Keep 5 backup files
    
    # Analytics Settings
    analytics_cache_ttl: int = 300  # Cache analytics for 5 minutes
    peak_hours_window: int = 1  # Hours to group for peak hour calculation
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create a global settings instance
settings = Settings()


def ensure_directories():
    """Create necessary directories if they don't exist."""
    settings.images_output_dir.mkdir(parents=True, exist_ok=True)
    settings.videos_output_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output and log directories created")


def setup_logging():
    """Configure application logging."""
    # Ensure logs directory exists
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file_path = settings.logs_dir / settings.log_file
    
    # Create logger
    logger = logging.getLogger("rickshaw_detection")
    logger.setLevel(getattr(logging, settings.log_level))
    
    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count
    )
    file_handler.setLevel(getattr(logging, settings.log_level))
    file_handler.setFormatter(logging.Formatter(settings.log_format))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level))
    console_handler.setFormatter(logging.Formatter(settings.log_format))
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logging()
