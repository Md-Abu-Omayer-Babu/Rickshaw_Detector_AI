"""
Video detection endpoint.
Handles POST /api/detect/video requests.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from app.db.models import VideoDetectionResponse, ErrorResponse
from app.services.video_service import VideoService
from app.core.startup import get_detector
from app.utils.file_utils import validate_video_file
from app.core.config import logger


# Create router
router = APIRouter(prefix="/detect", tags=["Detection"])


@router.post(
    "/video",
    response_model=VideoDetectionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file format"},
        500: {"model": ErrorResponse, "description": "Processing error"}
    },
    summary="Detect rickshaws in a video",
    description="Upload a video file to detect and count rickshaws frame by frame with entry/exit counting. Returns annotated video with bounding boxes and counts."
)
async def detect_video(
    file: UploadFile = File(..., description="Video file to process"),
    enable_counting: bool = Query(True, description="Enable entry/exit counting"),
    camera_id: str = Query("default", description="Camera identifier for logging")
):
    """
    Detect rickshaws in an uploaded video with entry/exit counting.
    
    - **file**: Video file (MP4, AVI, MOV, MKV)
    - **enable_counting**: Enable entry/exit line crossing detection (default: true)
    - **camera_id**: Camera identifier for database logging (default: "default")
    
    Returns:
    - **file_name**: Name of the processed output file
    - **rickshaw_count**: Maximum number of rickshaws detected in any frame
    - **total_entry**: Total entry count (if counting enabled)
    - **total_exit**: Total exit count (if counting enabled)
    - **net_count**: Net count (entry - exit)
    - **output_url**: URL to access the annotated video
    """
    try:
        logger.info(f"Video detection request: {file.filename}, counting={enable_counting}")
        
        # Validate file
        validate_video_file(file)
        
        # Get detector instance
        detector = get_detector()
        
        # Create video service
        video_service = VideoService(detector)
        
        # Process video
        result = await video_service.process_video(
            file=file,
            enable_counting=enable_counting,
            camera_id=camera_id
        )
        
        logger.info(f"Video processing complete: {result}")
        
        return VideoDetectionResponse(
            file_name=result["file_name"],
            rickshaw_count=result["rickshaw_count"],
            total_entry=result["total_entry"],
            total_exit=result["total_exit"],
            net_count=result["net_count"],
            output_url=result["output_url"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )
