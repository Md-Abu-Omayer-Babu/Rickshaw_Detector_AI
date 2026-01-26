from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.models import CCTVStreamRequest
from app.services.cctv_service import CCTVService
from app.core.startup import get_detector
from app.core.config import logger


# Create router
router = APIRouter(prefix="/cctv", tags=["CCTV Stream"])

class CCTVStartRequest(BaseModel):
    camera_id: str
    rtsp_url: str
    camera_name: Optional[str] = "Camera"


class CCTVStatusResponse(BaseModel):
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


@router.post(
    "/stream/test",
    summary="Test CCTV stream connection",
    description="Test connection to a CCTV/RTSP stream without full processing."
)
async def test_stream_connection(request: CCTVStreamRequest):
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
