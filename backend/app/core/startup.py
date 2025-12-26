"""
Startup module for initializing application components.
Handles model loading, database setup, and directory creation.
"""
from app.core.config import settings, ensure_directories, logger
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
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    
    # Create output directories
    print("\n📁 Setting up directories...")
    ensure_directories()
    logger.info("Directories initialized successfully")
    
    # Initialize database
    print("\n💾 Initializing database...")
    init_database()
    logger.info("Database initialized successfully")
    
    # Load YOLO model (ONCE at startup)
    print("\n🤖 Loading YOLO model...")
    print(f"   Model path: {settings.model_path}")
    print(f"   Device: {settings.yolo_device}")
    print(f"   Confidence: {settings.yolo_confidence}")
    print(f"   IoU: {settings.yolo_iou}")
    
    if not settings.model_path.exists():
        error_msg = f"YOLO model not found at {settings.model_path}"
        logger.error(error_msg)
        raise FileNotFoundError(
            f"{error_msg}. Please ensure best.pt is in the app/model/ directory."
        )
    
    detector_instance = YOLODetector(
        model_path=str(settings.model_path),
        confidence=settings.yolo_confidence,
        iou=settings.yolo_iou,
        device=settings.yolo_device
    )
    
    print("✓ Model loaded successfully!")
    logger.info("YOLO model loaded successfully")
    
    # Log entry-exit line configuration
    print(f"\n📏 Entry-Exit Line Configuration:")
    print(f"   Entry line: {settings.entry_line_start} → {settings.entry_line_end}")
    if settings.use_separate_lines:
        print(f"   Exit line: {settings.exit_line_start} → {settings.exit_line_end}")
    print(f"   Crossing threshold: {settings.crossing_threshold} pixels")
    logger.info(f"Entry-exit lines configured: {settings.entry_line_start} → {settings.entry_line_end}")
    
    print("\n" + "=" * 60)
    print("✅ Application startup complete!")
    print("=" * 60 + "\n")
    logger.info("Application startup complete")


def shutdown_event():
    """
    Cleanup on application shutdown.
    """
    global detector_instance
    print("\n🛑 Shutting down application...")
    logger.info("Shutting down application")
    detector_instance = None
    print("✓ Cleanup complete")
    logger.info("Application shutdown complete")


def get_detector() -> YOLODetector:
    """
    Get the global detector instance.
    
    Returns:
        YOLODetector: The loaded YOLO detector
        
    Raises:
        RuntimeError: If detector is not initialized
    """
    if detector_instance is None:
        error_msg = "Detector not initialized. Ensure startup_event() has been called."
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    return detector_instance
