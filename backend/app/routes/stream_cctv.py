"""
CCTV streaming endpoint for live preview.
Provides MJPEG stream of real-time CCTV camera frames.
"""
import cv2
import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.cctv_job_manager import get_cctv_job_manager
from app.core.config import logger


# Create router
router = APIRouter(prefix="/stream", tags=["CCTV Streaming"])


@router.get(
    "/cctv/{camera_id}",
    summary="Stream live CCTV camera frames (MJPEG)",
    description="Get live MJPEG stream of processed CCTV frames. Display using <img> tag."
)
async def stream_cctv(camera_id: str):
    """
    Stream live CCTV camera frames as MJPEG (Motion JPEG).
    This endpoint streams the latest processed frame continuously from a live camera.
    
    - **camera_id**: Camera identifier from /api/cctv/start
    
    Usage in frontend:
    <img src="/api/stream/cctv/{camera_id}" alt="Live CCTV Feed" />
    
    Returns:
    - Multipart MJPEG stream (image/jpeg frames)
    
    Note: Stream continues until camera is stopped or client disconnects.
    """
    try:
        job_manager = get_cctv_job_manager()
        job = job_manager.get_job(camera_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Camera not found: {camera_id}"
            )
        
        logger.info(f"[CCTV Stream {camera_id}] Starting MJPEG stream")
        
        def generate_mjpeg():
            """
            Generator function that yields MJPEG frames.
            Continuously sends the latest processed frame from live camera.
            """
            last_frame_data = None
            no_frame_count = 0
            max_no_frame_wait = 50  # Wait up to ~5 seconds for first frame
            
            while True:
                # Get current job state
                current_job = job_manager.get_job(camera_id)
                
                if not current_job:
                    logger.warning(f"[CCTV Stream {camera_id}] Camera no longer exists")
                    break
                
                # Check if camera was stopped
                if current_job.status == "stopped":
                    logger.info(f"[CCTV Stream {camera_id}] Camera stopped")
                    break
                
                # Check for error state
                if current_job.status == "error":
                    logger.warning(f"[CCTV Stream {camera_id}] Camera in error state: {current_job.error_message}")
                    break
                
                # Get latest processed frame
                frame = job_manager.get_latest_frame(camera_id)
                
                if frame is not None:
                    # Encode frame as JPEG
                    ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    
                    if ret:
                        frame_data = jpeg.tobytes()
                        
                        # Only send if frame has changed (optimization)
                        if frame_data != last_frame_data:
                            last_frame_data = frame_data
                            
                            # Yield frame in MJPEG format
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                            
                            no_frame_count = 0  # Reset counter when we get a frame
                else:
                    # No frame available yet - wait for processing to start
                    no_frame_count += 1
                    
                    if no_frame_count > max_no_frame_wait and current_job.status == "connecting":
                        logger.warning(f"[CCTV Stream {camera_id}] Still connecting, no frames yet")
                        # Don't break, keep waiting for connection
                
                # Rate limiting: ~10 FPS for MJPEG stream
                time.sleep(0.1)
        
        # Return streaming response
        return StreamingResponse(
            generate_mjpeg(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
        
    except Exception as e:
        logger.error(f"[CCTV Stream {camera_id}] Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error streaming camera: {str(e)}"
        )
