from fastapi import APIRouter, File, UploadFile, HTTPException
from app.db.models import ImageDetectionResponse, ErrorResponse
from app.services.inference_service import InferenceService
from app.core.startup import get_detector
from app.utils.file_utils import validate_image_file


# Create router
router = APIRouter(prefix="/detect", tags=["Detection"])


@router.post(
    "/image",
    response_model=ImageDetectionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file format"},
        500: {"model": ErrorResponse, "description": "Processing error"}
    },
    summary="Detect rickshaws in an image",
    description="Upload an image file to detect and count rickshaws. Returns annotated image with bounding boxes."
)
async def detect_image(file: UploadFile = File(..., description="Image file to process")):
    try:
        # Validate file
        validate_image_file(file)
        
        # Get detector instance
        detector = get_detector()
        
        # Create inference service
        inference_service = InferenceService(detector)
        
        # Process image
        result = await inference_service.process_image(file)
        
        return ImageDetectionResponse(
            file_name=result["file_name"],
            rickshaw_count=result["rickshaw_count"],
            output_url=result["output_url"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )
