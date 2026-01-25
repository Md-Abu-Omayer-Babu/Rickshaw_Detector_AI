from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Tuple, List, Dict
import logging
from logging.handlers import RotatingFileHandler


class Settings(BaseSettings):
    # Application Info
    app_name: str = "Smart Rickshaw Entry-Exit Monitoring System"
    version: str = "2.0.0"
    description: str = "FastAPI backend for rickshaw detection with entry-exit monitoring using YOLO"

    # API Settings
    api_prefix: str = "/api"
    debug: bool = True

    # CORS Settings
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

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
    yolo_device: str = "cpu"

    # Detection Settings
    target_class: str = "rickshaw"

    # Entry-Exit Line Settings (percentages)
    entry_line_start: Tuple[float, float] = (30.0, 50.0)
    entry_line_end: Tuple[float, float] = (70.0, 50.0)

    # Counting Settings
    crossing_threshold: int = 5
    min_detection_confidence: float = 0.3
    track_history_length: int = 30

    # Video Processing Optimization
    enable_live_preview: bool = False
    preview_update_interval: int = 5  # Update preview every N frames (0 = disabled)
    frame_skip: int = 5
    detection_scale_factor: float = 0.75
    use_fast_codec: bool = False

    # CCTV / RTSP Settings
    max_concurrent_streams: int = 4
    stream_reconnect_attempts: int = 3
    stream_reconnect_delay: int = 5
    stream_fps_limit: int = 15

    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "rickshaw_detection.log"
    log_max_bytes: int = 10 * 1024 * 1024  # 10 MB
    log_backup_count: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def ensure_directories():
    settings.images_output_dir.mkdir(parents=True, exist_ok=True)
    settings.videos_output_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)


def setup_logging():
    logger = logging.getLogger("rickshaw_detection")
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

        # Rotating file handler
        log_file_path = settings.logs_dir / settings.log_file
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count
        )
        file_handler.setFormatter(logging.Formatter(settings.log_format))
        file_handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(settings.log_format))
        console_handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Global logger instance
logger = setup_logging()
ensure_directories()
