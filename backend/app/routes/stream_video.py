"""
Video streaming endpoint for live preview.
Provides MJPEG stream of processed video frames.
"""
import cv2
import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.video_job_manager import get_job_manager
from app.core.config import logger


# Create router
router = APIRouter(prefix="/stream", tags=["Streaming"])


@router.get(
    "/video/{job_id}",
    summary="Stream live processed video frames (MJPEG)",
    description="Get live MJPEG stream of processed video frames for a job. Display using <img> tag."
)
async def stream_video(job_id: str):
    """
    Stream processed video frames as MJPEG (Motion JPEG).
    This endpoint streams the latest processed frame continuously.
    
    - **job_id**: Job identifier from /api/detect/video/async
    
    Usage in frontend:
    <img src="/api/stream/video/{job_id}" alt="Live Preview" />
    
    Returns:
    - Multipart MJPEG stream (image/jpeg frames)
    """
    try:
        job_manager = get_job_manager()
        job = job_manager.get_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job not found: {job_id}"
            )
        
        logger.info(f"[Stream {job_id}] Starting MJPEG stream")
        
        def generate_mjpeg():
            """
            Generator function that yields MJPEG frames.
            Continuously sends the latest processed frame.
            """
            last_frame_data = None
            no_frame_count = 0
            max_no_frame_attempts = 100  # Max attempts to wait for first frame
            
            while True:
                # Get current job state
                current_job = job_manager.get_job(job_id)
                
                if not current_job:
                    logger.warning(f"[Stream {job_id}] Job no longer exists")
                    break
                
                # Get latest processed frame
                frame = job_manager.get_latest_frame(job_id)
                
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
                    
                    if no_frame_count > max_no_frame_attempts:
                        logger.warning(f"[Stream {job_id}] No frames after {max_no_frame_attempts} attempts")
                        break
                
                # Check if job is completed or failed
                if current_job.status == "completed":
                    logger.info(f"[Stream {job_id}] Job completed, sending final frame")
                    # Send final frame one more time and exit
                    if frame is not None:
                        time.sleep(0.1)  # Small delay before closing
                    break
                
                elif current_job.status == "failed":
                    logger.warning(f"[Stream {job_id}] Job failed")
                    break
                
                # Small delay to control frame rate (adjust as needed)
                # ~10 FPS for live preview (100ms delay)
                time.sleep(0.1)
        
        # Return MJPEG stream
        return StreamingResponse(
            generate_mjpeg(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Stream {job_id}] Error streaming video: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error streaming video: {str(e)}"
        )
