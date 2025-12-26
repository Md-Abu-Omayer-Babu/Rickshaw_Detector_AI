"""
Startup module for initializing application components.
Handles model loading, database setup, and directory creation.
"""
from app.core.config import settings, ensure_directories
from app.db.database import init_database
from app.model.detector import YOLODetector


# Global detector instance
detector_instance: YOLODetector | None = None


def startup_event():
    """
    Initialize all application components at startup.
    This function is called once when the application starts.
    """
    global detector_instance
    
    print("=" * 60)
    print(f"🚀 Starting {settings.app_name} v{settings.version}")
    print("=" * 60)
    
    # Create output directories
    print("\n📁 Setting up directories...")
    ensure_directories()
    
    # Initialize database
    print("\n💾 Initializing database...")
    init_database()
    
    # Load YOLO model (ONCE at startup)
    print("\n🤖 Loading YOLO model...")
    print(f"   Model path: {settings.model_path}")
    print(f"   Device: {settings.yolo_device}")
    
    if not settings.model_path.exists():
        raise FileNotFoundError(
            f"YOLO model not found at {settings.model_path}. "
            "Please ensure best.pt is in the app/model/ directory."
        )
    
    detector_instance = YOLODetector(
        model_path=str(settings.model_path),
        confidence=settings.yolo_confidence,
        iou=settings.yolo_iou,
        device=settings.yolo_device
    )
    
    print("✓ Model loaded successfully!")
    print("\n" + "=" * 60)
    print("✅ Application startup complete!")
    print("=" * 60 + "\n")


def shutdown_event():
    """
    Cleanup on application shutdown.
    """
    global detector_instance
    print("\n🛑 Shutting down application...")
    detector_instance = None
    print("✓ Cleanup complete")


def get_detector() -> YOLODetector:
    """
    Get the global detector instance.
    
    Returns:
        YOLODetector: The loaded YOLO detector
        
    Raises:
        RuntimeError: If detector is not initialized
    """
    if detector_instance is None:
        raise RuntimeError(
            "Detector not initialized. Ensure startup_event() has been called."
        )
    return detector_instance
