"""
Video detection endpoint.
Handles POST /api/detect/video requests.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.db.models import VideoDetectionResponse, ErrorResponse
from app.services.video_service import VideoService
from app.core.startup import get_detector
from app.utils.file_utils import validate_video_file


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
    description="Upload a video file to detect and count rickshaws frame by frame. Returns annotated video with bounding boxes."
)
async def detect_video(file: UploadFile = File(..., description="Video file to process")):
    """
    Detect rickshaws in an uploaded video.
    
    - **file**: Video file (MP4, AVI, MOV, MKV)
    
    Returns:
    - **file_name**: Name of the processed output file
    - **rickshaw_count**: Maximum number of rickshaws detected in any frame
    - **output_url**: URL to access the annotated video
    """
    try:
        # Validate file
        validate_video_file(file)
        
        # Get detector instance
        detector = get_detector()
        
        # Create video service
        video_service = VideoService(detector)
        
        # Process video
        result = await video_service.process_video(file)
        
        return VideoDetectionResponse(
            file_name=result["file_name"],
            rickshaw_count=result["rickshaw_count"],
            output_url=result["output_url"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )
