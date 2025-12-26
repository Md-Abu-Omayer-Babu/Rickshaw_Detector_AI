"""
CCTV/RTSP stream detection endpoint.
Handles real-time detection from camera streams.
"""
from fastapi import APIRouter, HTTPException
from app.db.models import CCTVStreamRequest, CCTVStreamResponse, ErrorResponse
from app.services.cctv_service import CCTVService
from app.core.startup import get_detector
from app.core.config import logger


# Create router
router = APIRouter(prefix="/cctv", tags=["CCTV Stream"])


@router.post(
    "/stream",
    response_model=CCTVStreamResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Processing error"}
    },
    summary="Process CCTV/RTSP stream",
    description="Process a live CCTV or RTSP stream with real-time rickshaw detection and entry/exit counting."
)
async def process_cctv_stream(request: CCTVStreamRequest):
    """
    Process a CCTV/RTSP stream for real-time detection.
    
    - **camera_id**: Unique identifier for the camera
    - **rtsp_url**: RTSP stream URL (e.g., rtsp://admin:password@192.168.1.100:554/stream1)
    - **duration**: Duration to process in seconds (default: 60)
    - **camera_name**: Human-readable camera name (optional)
    
    Returns:
    - Total entry count
    - Total exit count
    - Net count
    - Number of frames processed
    - Processing duration
    
    Note: This endpoint processes the stream for the specified duration and then returns.
    For continuous monitoring, consider using a background service.
    """
    try:
        logger.info(f"Starting CCTV stream processing: camera={request.camera_id}, "
                   f"duration={request.duration}s")
        
        # Get detector instance
        detector = get_detector()
        
        # Create CCTV service
        cctv_service = CCTVService(detector)
        
        # Process stream (this will block for the duration)
        stats = await cctv_service.start_stream(
            camera_id=request.camera_id,
            rtsp_url=request.rtsp_url,
            duration=request.duration,
            camera_name=request.camera_name or request.camera_id
        )
        
        logger.info(f"CCTV stream processing complete: {stats}")
        
        return CCTVStreamResponse(
            camera_id=stats['camera_id'],
            total_entry=stats['total_entry'],
            total_exit=stats['total_exit'],
            net_count=stats['net_count'],
            frames_processed=stats['frames_processed'],
            duration=stats['duration']
        )
        
    except RuntimeError as e:
        logger.error(f"Runtime error processing CCTV stream: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing CCTV stream: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing stream: {str(e)}"
        )


@router.post(
    "/stream/test",
    summary="Test CCTV stream connection",
    description="Test connection to a CCTV/RTSP stream without full processing."
)
async def test_stream_connection(request: CCTVStreamRequest):
    """
    Test connection to a CCTV/RTSP stream.
    
    - **camera_id**: Unique identifier for the camera
    - **rtsp_url**: RTSP stream URL
    
    Returns:
    - Connection status
    - Stream properties (if successful)
    """
    try:
        import cv2
        
        logger.info(f"Testing stream connection: {request.rtsp_url}")
        
        cap = cv2.VideoCapture(request.rtsp_url)
        
        if not cap.isOpened():
            logger.warning(f"Failed to connect to stream: {request.rtsp_url}")
            return {
                "success": False,
                "message": "Failed to connect to stream",
                "camera_id": request.camera_id
            }
        
        # Get stream properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Try to read one frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            logger.warning(f"Connected but failed to read frame: {request.rtsp_url}")
            return {
                "success": False,
                "message": "Connected but failed to read frame",
                "camera_id": request.camera_id
            }
        
        logger.info(f"Stream connection successful: {width}x{height} @ {fps}fps")
        
        return {
            "success": True,
            "message": "Stream connection successful",
            "camera_id": request.camera_id,
            "stream_properties": {
                "width": width,
                "height": height,
                "fps": fps
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing stream connection: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "camera_id": request.camera_id
        }
