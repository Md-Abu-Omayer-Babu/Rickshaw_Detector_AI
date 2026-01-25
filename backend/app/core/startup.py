from app.core.config import settings, ensure_directories, logger
from app.db.database import init_database
from app.model.detector import YOLODetector


# Global detector instance
detector_instance: YOLODetector | None = None


def startup_event():
    global detector_instance

    logger.info(f"Starting {settings.app_name} v{settings.version}")
    
    # Create output directories
    ensure_directories()
    logger.info("Directories initialized successfully")
    
    # Initialize database
    print("\nInitializing database...")
    init_database()
    logger.info("Database initialized successfully")
    
    # Load YOLO model (ONCE at startup)
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
    
    print("Model loaded successfully!")
    logger.info("YOLO model loaded successfully")
    
    # Log entry-exit line configuration
    logger.info(f"Entry-exit lines configured: {settings.entry_line_start} → {settings.entry_line_end}")
    
    logger.info("Application startup complete")


def shutdown_event():
    global detector_instance
    print("\nShutting down application...")
    logger.info("Shutting down application")
    detector_instance = None
    print("Cleanup complete")
    logger.info("Application shutdown complete")


def get_detector() -> YOLODetector:
    if detector_instance is None:
        error_msg = "Detector not initialized. Ensure startup_event() has been called."
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    return detector_instance
