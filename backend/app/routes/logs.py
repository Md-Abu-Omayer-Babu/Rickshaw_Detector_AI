"""
Rickshaw logs endpoint.
Provides access to entry/exit event logs with filtering options.
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional, List
from app.db.models import RickshawLogRecord, ErrorResponse
from app.db.database import get_rickshaw_logs
from app.core.config import logger


# Create router
router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get(
    "",
    response_model=dict,
    responses={
        500: {"model": ErrorResponse, "description": "Database error"}
    },
    summary="Get rickshaw event logs",
    description="Retrieve rickshaw entry/exit event logs with optional filtering by date range, event type, and camera."
)
async def get_logs(
    start_date: Optional[str] = Query(
        None,
        description="Start date filter (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
        example="2024-01-01"
    ),
    end_date: Optional[str] = Query(
        None,
        description="End date filter (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
        example="2024-12-31"
    ),
    event_type: Optional[str] = Query(
        None,
        description="Filter by event type",
        example="entry",
        regex="^(entry|exit)$"
    ),
    camera_id: Optional[str] = Query(
        None,
        description="Filter by camera ID",
        example="camera_01"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of records to return"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of records to skip"
    )
):
    """
    Get rickshaw event logs with filters.
    
    Query Parameters:
    - **start_date**: Filter events from this date onwards (optional)
    - **end_date**: Filter events up to this date (optional)
    - **event_type**: Filter by 'entry' or 'exit' (optional)
    - **camera_id**: Filter by specific camera (optional)
    - **limit**: Maximum records to return (1-1000, default: 100)
    - **offset**: Number of records to skip for pagination (default: 0)
    
    Returns:
    - **total**: Total number of matching records
    - **count**: Number of records in this response
    - **logs**: List of log records
    - **filters_applied**: Summary of applied filters
    """
    try:
        logger.info(
            f"Fetching logs: start={start_date}, end={end_date}, "
            f"type={event_type}, camera={camera_id}, limit={limit}, offset={offset}"
        )
        
        # Parse dates if provided
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid start_date format. Use ISO format (e.g., '2024-01-01' or '2024-01-01T00:00:00')"
                )
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid end_date format. Use ISO format (e.g., '2024-12-31' or '2024-12-31T23:59:59')"
                )
        
        # Validate date range
        if start_datetime and end_datetime and start_datetime > end_datetime:
            raise HTTPException(
                status_code=400,
                detail="start_date must be before end_date"
            )
        
        # Fetch logs from database
        logs = get_rickshaw_logs(
            start_date=start_datetime,
            end_date=end_datetime,
            event_type=event_type,
            camera_id=camera_id,
            limit=limit,
            offset=offset
        )
        
        # Convert to response models
        log_records = [
            RickshawLogRecord(
                id=log["id"],
                timestamp=log["timestamp"],
                event_type=log["event_type"],
                camera_id=log["camera_id"],
                confidence=log["confidence"],
                bbox_x1=log["bbox_x1"],
                bbox_y1=log["bbox_y1"],
                bbox_x2=log["bbox_x2"],
                bbox_y2=log["bbox_y2"]
            )
            for log in logs
        ]
        
        # Build filters summary
        filters_applied = {}
        if start_date:
            filters_applied["start_date"] = start_date
        if end_date:
            filters_applied["end_date"] = end_date
        if event_type:
            filters_applied["event_type"] = event_type
        if camera_id:
            filters_applied["camera_id"] = camera_id
        
        logger.info(f"Retrieved {len(log_records)} logs")
        
        return {
            "total": len(log_records),  # Note: This is the count returned, not total in DB
            "count": len(log_records),
            "offset": offset,
            "limit": limit,
            "logs": log_records,
            "filters_applied": filters_applied if filters_applied else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving logs: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=dict,
    summary="Get log statistics",
    description="Get quick statistics about the event logs."
)
async def get_log_stats():
    """
    Get statistics about logged events.
    
    Returns:
    - **total_events**: Total number of logged events
    - **entry_count**: Total entry events
    - **exit_count**: Total exit events
    - **cameras**: List of camera IDs that have logged events
    """
    try:
        # Fetch all logs (up to reasonable limit for stats)
        all_logs = get_rickshaw_logs(limit=10000)
        
        # Calculate statistics
        total_events = len(all_logs)
        entry_count = sum(1 for log in all_logs if log["event_type"] == "entry")
        exit_count = sum(1 for log in all_logs if log["event_type"] == "exit")
        cameras = list(set(log["camera_id"] for log in all_logs))
        
        logger.info(f"Log stats: total={total_events}, entry={entry_count}, exit={exit_count}")
        
        return {
            "total_events": total_events,
            "entry_count": entry_count,
            "exit_count": exit_count,
            "net_count": entry_count - exit_count,
            "cameras": cameras,
            "camera_count": len(cameras)
        }
        
    except Exception as e:
        logger.error(f"Error calculating log stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving log statistics: {str(e)}"
        )
