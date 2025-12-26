"""
History endpoint.
Handles GET /api/history requests.
"""
from fastapi import APIRouter, HTTPException
from app.db.models import HistoryResponse, DetectionRecord, ErrorResponse
from app.db.database import get_all_detections


# Create router
router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "",
    response_model=HistoryResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Database error"}
    },
    summary="Get detection history",
    description="Retrieve all detection records from the database, ordered by most recent first."
)
async def get_history():
    """
    Get all detection history records.
    
    Returns:
    - **total_records**: Total number of detection records
    - **detections**: List of all detection records with details
    """
    try:
        # Fetch all detections from database
        detections = get_all_detections()
        
        # Convert to Pydantic models
        detection_records = [DetectionRecord(**record) for record in detections]
        
        return HistoryResponse(
            total_records=len(detection_records),
            detections=detection_records
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching history: {str(e)}"
        )
