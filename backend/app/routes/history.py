from fastapi import APIRouter, HTTPException, Query
from typing import Optional
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
    summary="Get detection history with filters",
    description="Retrieve detection records with optional filters for date range and file type."
)
async def get_history(
    start_date: Optional[str] = Query(
        None,
        pattern="^\\d{4}-\\d{2}-\\d{2}$",
        description="Start date in YYYY-MM-DD format",
        examples=["2025-01-01"]
    ),
    end_date: Optional[str] = Query(
        None,
        pattern="^\\d{4}-\\d{2}-\\d{2}$",
        description="End date in YYYY-MM-DD format",
        examples=["2025-12-31"]
    ),
    file_type: Optional[str] = Query(
        None,
        pattern="^(image|video)$",
        description="Filter by file type: 'image' or 'video'",
        examples=["image"]
    )
):
    try:
        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date cannot be after end_date"
            )
        
        # Fetch detections with filters
        detections = get_all_detections(
            start_date=start_date,
            end_date=end_date,
            file_type=file_type
        )
        
        # Convert to Pydantic models
        detection_records = [DetectionRecord(**record) for record in detections]
        
        return HistoryResponse(
            total_records=len(detection_records),
            detections=detection_records
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching history: {str(e)}"
        )
