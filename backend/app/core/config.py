"""
Configuration module for the FastAPI application.
Contains all application settings and environment configurations.
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application Info
    app_name: str = "Rickshaw Detection API"
    version: str = "1.0.0"
    description: str = "FastAPI backend for detecting rickshaws in images and videos using YOLO"
    
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
    outputs_dir: Path = base_dir / "app" / "outputs"
    images_output_dir: Path = outputs_dir / "images"
    videos_output_dir: Path = outputs_dir / "videos"
    database_path: Path = base_dir / "detections.db"
    
    # YOLO Settings
    yolo_confidence: float = 0.25
    yolo_iou: float = 0.45
    yolo_device: str = "cpu"  # Change to "cuda" if GPU is available
    
    # Detection Settings
    target_class: str = "rickshaw"  # Class name to detect
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create a global settings instance
settings = Settings()


def ensure_directories():
    """Create necessary directories if they don't exist."""
    settings.images_output_dir.mkdir(parents=True, exist_ok=True)
    settings.videos_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directories created at {settings.outputs_dir}")
