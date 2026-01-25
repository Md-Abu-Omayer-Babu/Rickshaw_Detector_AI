from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from app.services.webcam_service import get_webcam_service
from app.core.config import logger


router = APIRouter(prefix="/api/webcam", tags=["Webcam Streaming"])


class WebcamStartRequest(BaseModel):
    camera_index: int = Field(default=0, ge=0, description="Camera device index (0 for default)")
    camera_name: str = Field(default="Webcam", description="Display name for camera")
    frame_skip: int = Field(default=3, ge=1, le=10, description="Process every Nth frame")


class WebcamStopRequest(BaseModel):
    camera_index: int = Field(default=0, ge=0, description="Camera device index")


@router.post("/start", summary="Start Webcam Stream")
async def start_webcam(request: WebcamStartRequest):
    try:
        logger.info(f"Starting webcam stream: camera={request.camera_index}, skip={request.frame_skip}")
        
        webcam_service = get_webcam_service()
        result = webcam_service.start_stream(
            camera_index=request.camera_index,
            camera_name=request.camera_name,
            frame_skip=request.frame_skip
        )
        
        return {
            "success": True,
            "message": "Webcam stream started successfully",
            "camera_index": request.camera_index,
            "camera_name": request.camera_name,
            "stream_properties": {
                "width": result.get("width"),
                "height": result.get("height"),
                "fps": result.get("fps")
            },
            "config": {
                "frame_skip": request.frame_skip
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to start webcam: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", summary="Stop Webcam Stream")
async def stop_webcam(request: WebcamStopRequest):
    try:
        logger.info(f"Stopping webcam stream: camera={request.camera_index}")
        
        webcam_service = get_webcam_service()
        result = webcam_service.stop_stream(request.camera_index)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail="Stream not found")
        
        return {
            "success": True,
            "message": f"Webcam {request.camera_index} stopped successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop webcam: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{camera_index}", summary="Get Webcam Status")
async def get_webcam_status(camera_index: int = 0):
    try:
        webcam_service = get_webcam_service()
        status = webcam_service.get_status(camera_index)
        
        return {
            "success": True,
            **status
        }
        
    except Exception as e:
        logger.error(f"Failed to get webcam status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", summary="List Active Webcam Streams")
async def list_webcam_streams():
    try:
        webcam_service = get_webcam_service()
        result = webcam_service.list_streams()
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list webcam streams: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{camera_index}", summary="MJPEG Video Stream")
async def stream_webcam(camera_index: int = 0):
    try:
        webcam_service = get_webcam_service()
        processor = webcam_service.get_stream_processor(camera_index)
        
        if not processor:
            raise HTTPException(
                status_code=404,
                detail=f"No active stream for camera {camera_index}. Start the stream first."
            )
        
        logger.info(f"Streaming webcam: camera={camera_index}")
        
        return StreamingResponse(
            processor.process_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cameras", summary="List Available Cameras")
async def list_available_cameras():
    import cv2
    
    available_cameras = []
    
    # Test camera indices 0-4
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append({
                "index": i,
                "name": f"Camera {i}"
            })
            cap.release()
    
    return {
        "success": True,
        "count": len(available_cameras),
        "cameras": available_cameras
    }
