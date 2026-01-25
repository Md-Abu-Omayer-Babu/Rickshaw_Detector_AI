"""
Webcam streaming API routes.
Provides endpoints for real-time webcam detection with MJPEG streaming.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from app.services.webcam_service import get_webcam_service
from app.core.config import logger


router = APIRouter(prefix="/api/webcam", tags=["Webcam Streaming"])


class WebcamStartRequest(BaseModel):
    """Request model for starting webcam stream"""
    camera_index: int = Field(default=0, ge=0, description="Camera device index (0 for default)")
    camera_name: str = Field(default="Webcam", description="Display name for camera")
    frame_skip: int = Field(default=3, ge=1, le=10, description="Process every Nth frame")


class WebcamStopRequest(BaseModel):
    """Request model for stopping webcam stream"""
    camera_index: int = Field(default=0, ge=0, description="Camera device index")


@router.post("/start", summary="Start Webcam Stream")
async def start_webcam(request: WebcamStartRequest):
    """
    Start real-time webcam streaming with YOLOv8 detection.
    
    **Features:**
    - Frame skipping for performance (configurable)
    - Real-time rickshaw detection
    - Entry/exit counting
    - MJPEG video streaming
    
    **Parameters:**
    - **camera_index**: Webcam device index (0 for default, 1, 2, etc. for additional cameras)
    - **camera_name**: Display name for the camera
    - **frame_skip**: Process every Nth frame (higher = faster but less accurate)
    
    **Returns:**
    - Success status and stream properties
    
    **Example:**
    ```json
    {
        "camera_index": 0,
        "camera_name": "Front Camera",
        "frame_skip": 3
    }
    ```
    """
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
    """
    Stop an active webcam stream.
    
    **Parameters:**
    - **camera_index**: Camera device index to stop
    
    **Returns:**
    - Success status
    """
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
    """
    Get real-time status of a webcam stream.
    
    **Returns:**
    - Stream status (streaming/stopped)
    - Live counts (entry/exit/net)
    - FPS and performance metrics
    - Frames processed statistics
    
    **Use this endpoint for polling (every 1-2 seconds) to update UI**
    """
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
    """
    List all active webcam streams.
    
    **Returns:**
    - Count of active streams
    - List of stream details with status
    """
    try:
        webcam_service = get_webcam_service()
        result = webcam_service.list_streams()
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list webcam streams: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{camera_index}", summary="MJPEG Video Stream")
async def stream_webcam(camera_index: int = 0):
    """
    Get MJPEG video stream with YOLOv8 detections.
    
    **Returns:**
    - MJPEG stream (multipart/x-mixed-replace)
    - Annotated frames with bounding boxes
    - Real-time entry/exit counts overlay
    
    **Usage in HTML:**
    ```html
    <img src="/api/webcam/stream/0" alt="Webcam Stream" />
    ```
    
    **Usage in React:**
    ```jsx
    <img src={`http://localhost:8000/api/webcam/stream/${cameraIndex}`} />
    ```
    """
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
    """
    Detect available camera devices on the system.
    
    **Returns:**
    - List of available camera indices
    
    **Note:** This is a simple detection that tests indices 0-4.
    """
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
