"""
CCTV/RTSP stream detection endpoint.
Handles both batch processing (legacy) and continuous streaming (live preview).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.models import CCTVStreamRequest, CCTVStreamResponse, ErrorResponse
from app.services.cctv_service import CCTVService
from app.core.startup import get_detector
from app.core.config import logger


# Create router
router = APIRouter(prefix="/cctv", tags=["CCTV Stream"])


# ========================================
# NEW: Continuous Streaming Endpoints (Live Preview)
# ========================================

class CCTVStartRequest(BaseModel):
    """Request schema for starting continuous CCTV stream."""
    camera_id: str
    rtsp_url: str
    camera_name: Optional[str] = "Camera"


class CCTVStatusResponse(BaseModel):
    """Response schema for CCTV stream status."""
    success: bool = True
    camera_id: str
    camera_name: str
    status: str
    entry_count: int
    exit_count: int
    net_count: int
    frames_processed: int
    fps: float
    uptime: float
    stream_properties: Optional[dict] = None
    error_message: Optional[str] = None


@router.post(
    "/start",
    summary="Start continuous CCTV stream with live preview",
    description="Start a continuous CCTV/RTSP stream that can be viewed in real-time via MJPEG."
)
async def start_cctv_stream(request: CCTVStartRequest):
    """
    Start continuous CCTV stream processing with live preview.
    Stream continues until explicitly stopped via /api/cctv/stop/{camera_id}.
    
    - **camera_id**: Unique identifier for the camera
    - **rtsp_url**: RTSP stream URL (e.g., rtsp://admin:password@192.168.1.100:554/stream1)
    - **camera_name**: Human-readable camera name (optional)
    
    Returns:
    - Immediate response with camera info
    - Stream status: "connecting" → "streaming"
    - Access live feed: GET /api/stream/cctv/{camera_id}
    - Poll status: GET /api/cctv/status/{camera_id}
    
    Note: This is for continuous streaming with live preview, not batch processing.
    For batch processing, use /api/cctv/stream endpoint.
    """
    try:
        logger.info(f"Starting continuous CCTV stream: camera={request.camera_id}")
        
        # Get detector instance
        detector = get_detector()
        
        # Create CCTV service
        cctv_service = CCTVService(detector)
        
        # Start continuous stream (non-blocking)
        result = cctv_service.start_continuous_stream(
            camera_id=request.camera_id,
            rtsp_url=request.rtsp_url,
            camera_name=request.camera_name or request.camera_id
        )
        
        logger.info(f"Continuous stream started: {result}")
        return result
        
    except RuntimeError as e:
        logger.error(f"Runtime error starting CCTV stream: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting CCTV stream: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error starting stream: {str(e)}")


@router.post(
    "/stop/{camera_id}",
    summary="Stop continuous CCTV stream",
    description="Stop a running continuous CCTV stream."
)
async def stop_cctv_stream(camera_id: str):
    """
    Stop a continuous CCTV stream.
    
    - **camera_id**: Camera identifier
    
    Returns:
    - Confirmation of stream stop
    """
    try:
        logger.info(f"Stopping continuous CCTV stream: camera={camera_id}")
        
        # Get detector instance
        detector = get_detector()
        
        # Create CCTV service
        cctv_service = CCTVService(detector)
        
        # Stop stream
        result = cctv_service.stop_continuous_stream(camera_id)
        
        logger.info(f"Stream stopped: {result}")
        return result
        
    except RuntimeError as e:
        logger.error(f"Runtime error stopping stream: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error stopping stream: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error stopping stream: {str(e)}")


@router.get(
    "/status/{camera_id}",
    response_model=CCTVStatusResponse,
    summary="Get CCTV stream status",
    description="Get current status and statistics of a continuous CCTV stream."
)
async def get_cctv_status(camera_id: str):
    """
    Get the current status of a continuous CCTV stream.
    Poll this endpoint every 2 seconds for live updates.
    
    - **camera_id**: Camera identifier
    
    Returns:
    - Stream status: idle | connecting | streaming | stopped | error
    - Live counts: entry_count, exit_count, net_count
    - Performance metrics: fps, uptime, frames_processed
    - Stream properties: width, height, fps
    """
    try:
        # Get detector instance
        detector = get_detector()
        
        # Create CCTV service
        cctv_service = CCTVService(detector)
        
        # Get status
        status = cctv_service.get_stream_status(camera_id)
        
        return status
        
    except RuntimeError as e:
        logger.error(f"Runtime error getting status: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@router.get(
    "/list",
    summary="List all active CCTV streams",
    description="Get list of all currently active continuous streams."
)
async def list_cctv_streams():
    """
    List all active continuous CCTV streams.
    
    Returns:
    - List of all active camera streams with their status
    """
    try:
        # Get detector instance
        detector = get_detector()
        
        # Create CCTV service
        cctv_service = CCTVService(detector)
        
        # Get list
        result = cctv_service.list_active_streams()
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing streams: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing streams: {str(e)}")


# ========================================
# Legacy Batch Processing Endpoint (Preserved)
# ========================================


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
