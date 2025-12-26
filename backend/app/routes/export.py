"""
Data export endpoint.
Provides functionality to export rickshaw logs in CSV or JSON format.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime
from typing import Optional
import io
import csv
import json
from app.db.database import get_rickshaw_logs
from app.core.config import logger


# Create router
router = APIRouter(prefix="/export", tags=["Export"])


@router.get(
    "/logs",
    summary="Export rickshaw logs",
    description="Export rickshaw event logs as CSV or JSON with optional filtering."
)
async def export_logs(
    format: str = Query(
        "csv",
        description="Export format",
        pattern="^(csv|json)$"
    ),
    start_date: Optional[str] = Query(
        None,
        description="Start date filter (ISO format: YYYY-MM-DD)",
        examples=["2024-01-01"]
    ),
    end_date: Optional[str] = Query(
        None,
        description="End date filter (ISO format: YYYY-MM-DD)",
        examples=["2024-12-31"]
    ),
    event_type: Optional[str] = Query(
        None,
        description="Filter by event type",
        pattern="^(entry|exit)$"
    ),
    camera_id: Optional[str] = Query(
        None,
        description="Filter by camera ID"
    ),
    limit: int = Query(
        10000,
        ge=1,
        le=100000,
        description="Maximum number of records to export"
    )
):
    """
    Export rickshaw logs to CSV or JSON.
    
    Query Parameters:
    - **format**: Export format - 'csv' or 'json' (default: csv)
    - **start_date**: Filter from this date (optional)
    - **end_date**: Filter to this date (optional)
    - **event_type**: Filter by 'entry' or 'exit' (optional)
    - **camera_id**: Filter by camera (optional)
    - **limit**: Max records (1-100000, default: 10000)
    
    Returns:
    - CSV or JSON file for download
    """
    try:
        logger.info(
            f"Export request: format={format}, start={start_date}, "
            f"end={end_date}, type={event_type}, camera={camera_id}"
        )
        
        # Parse dates
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid start_date format. Use YYYY-MM-DD"
                )
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid end_date format. Use YYYY-MM-DD"
                )
        
        # Fetch logs
        logs = get_rickshaw_logs(
            start_date=start_datetime,
            end_date=end_datetime,
            event_type=event_type,
            camera_id=camera_id,
            limit=limit
        )
        
        if not logs:
            raise HTTPException(
                status_code=404,
                detail="No logs found matching the specified criteria"
            )
        
        logger.info(f"Exporting {len(logs)} logs as {format.upper()}")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rickshaw_logs_{timestamp}.{format}"
        
        # Export as CSV
        if format == "csv":
            return _export_as_csv(logs, filename)
        
        # Export as JSON
        elif format == "json":
            return _export_as_json(logs, filename)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting logs: {str(e)}"
        )


def _export_as_csv(logs: list, filename: str) -> StreamingResponse:
    """
    Export logs as CSV file.
    
    Args:
        logs: List of log dictionaries
        filename: Name for the downloaded file
        
    Returns:
        StreamingResponse with CSV data
    """
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "id", "timestamp", "event_type", "camera_id",
            "confidence", "bbox_x1", "bbox_y1", "bbox_x2", "bbox_y2"
        ]
    )
    
    # Write header and data
    writer.writeheader()
    writer.writerows(logs)
    
    # Prepare response
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


def _export_as_json(logs: list, filename: str) -> StreamingResponse:
    """
    Export logs as JSON file.
    
    Args:
        logs: List of log dictionaries
        filename: Name for the downloaded file
        
    Returns:
        StreamingResponse with JSON data
    """
    # Create JSON structure
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "record_count": len(logs),
        "logs": logs
    }
    
    # Convert to JSON string
    json_str = json.dumps(export_data, indent=2, default=str)
    
    return StreamingResponse(
        iter([json_str]),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get(
    "/analytics",
    summary="Export analytics summary",
    description="Export daily and hourly analytics as CSV or JSON."
)
async def export_analytics(
    format: str = Query(
        "csv",
        description="Export format",
        pattern="^(csv|json)$"
    ),
    days: int = Query(
        30,
        ge=1,
        le=365,
        description="Number of past days to include"
    )
):
    """
    Export analytics summary.
    
    Query Parameters:
    - **format**: Export format - 'csv' or 'json' (default: csv)
    - **days**: Number of past days to include (1-365, default: 30)
    
    Returns:
    - CSV or JSON file with daily statistics
    """
    try:
        from app.db.database import get_daily_counts
        
        logger.info(f"Exporting analytics: format={format}, days={days}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch daily counts
        daily_data = get_daily_counts(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        if not daily_data:
            raise HTTPException(
                status_code=404,
                detail="No analytics data found for the specified period"
            )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analytics_{timestamp}.{format}"
        
        logger.info(f"Exporting {len(daily_data)} days of analytics")
        
        # Export based on format
        if format == "csv":
            return _export_analytics_csv(daily_data, filename)
        else:
            return _export_analytics_json(daily_data, filename)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting analytics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting analytics: {str(e)}"
        )


def _export_analytics_csv(data: list, filename: str) -> StreamingResponse:
    """Export analytics as CSV."""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["date", "entry_count", "exit_count", "net_count"]
    )
    
    writer.writeheader()
    writer.writerows(data)
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


def _export_analytics_json(data: list, filename: str) -> StreamingResponse:
    """Export analytics as JSON."""
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "record_count": len(data),
        "analytics": data
    }
    
    json_str = json.dumps(export_data, indent=2, default=str)
    
    return StreamingResponse(
        iter([json_str]),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# Import timedelta for date calculations
from datetime import timedelta
