from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from app.db.models import (
    AnalyticsDashboard, DailyCounts, HourlyCount, 
    PeakHourInfo, ErrorResponse
)
from app.db.database import (
    get_total_counts, get_daily_counts, get_hourly_distribution
)
from app.core.config import logger


# Create router
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/dashboard",
    response_model=AnalyticsDashboard,
    responses={500: {"model": ErrorResponse, "description": "Server error"}},
    summary="Get analytics dashboard data",
    description="Retrieve comprehensive analytics including total counts, today's stats, hourly distribution, and daily trends."
)
async def get_dashboard(
    camera_id: str = Query("default", description="Camera ID to filter by")
):
    try:
        logger.info(f"Fetching dashboard analytics for camera: {camera_id}")
        
        # Get total counts (all time)
        total_stats = get_total_counts(camera_id)
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get today's counts
        today_stats = get_daily_counts(today, camera_id)
        
        # Get hourly distribution for today
        hourly_data = get_hourly_distribution(today, camera_id)
        hourly_counts = [HourlyCount(**row) for row in hourly_data]
        
        # Calculate peak hour
        peak_hour_info = None
        if hourly_data:
            # Group by hour and sum entry + exit
            hour_totals = {}
            for row in hourly_data:
                hour = int(row['hour'])
                if hour not in hour_totals:
                    hour_totals[hour] = {'entry': 0, 'exit': 0, 'total': 0}
                
                if row['event_type'] == 'entry':
                    hour_totals[hour]['entry'] = row['count']
                elif row['event_type'] == 'exit':
                    hour_totals[hour]['exit'] = row['count']
                
                hour_totals[hour]['total'] = (hour_totals[hour]['entry'] + 
                                             hour_totals[hour]['exit'])
            
            # Find peak hour
            if hour_totals:
                peak_hour = max(hour_totals.items(), key=lambda x: x[1]['total'])
                peak_hour_info = PeakHourInfo(
                    hour=peak_hour[0],
                    entry_count=peak_hour[1]['entry'],
                    exit_count=peak_hour[1]['exit'],
                    total_count=peak_hour[1]['total']
                )
        
        # Get daily trend (last 7 days)
        daily_trend = []
        for i in range(6, -1, -1):  # Last 7 days including today
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_stats = get_daily_counts(date, camera_id)
            daily_trend.append(DailyCounts(**day_stats))
        
        logger.info(f"Dashboard analytics fetched successfully")
        
        return AnalyticsDashboard(
            total_entry=total_stats['total_entry'],
            total_exit=total_stats['total_exit'],
            net_count=total_stats['net_count'],
            today_entry=today_stats['entry_count'],
            today_exit=today_stats['exit_count'],
            today_net=today_stats['net_count'],
            hourly_distribution=hourly_counts,
            peak_hour=peak_hour_info,
            daily_trend=daily_trend
        )
        
    except Exception as e:
        logger.error(f"Error fetching dashboard analytics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching analytics: {str(e)}"
        )


@router.get(
    "/daily",
    response_model=DailyCounts,
    responses={500: {"model": ErrorResponse, "description": "Server error"}},
    summary="Get daily counts",
    description="Get entry/exit counts for a specific date."
)
async def get_daily_stats(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    camera_id: str = Query("default", description="Camera ID to filter by")
):
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
        
        logger.info(f"Fetching daily stats for date: {date}, camera: {camera_id}")
        
        stats = get_daily_counts(date, camera_id)
        
        return DailyCounts(**stats)
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD."
        )
    except Exception as e:
        logger.error(f"Error fetching daily stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching daily stats: {str(e)}"
        )


@router.get(
    "/hourly",
    response_model=list[HourlyCount],
    responses={500: {"model": ErrorResponse, "description": "Server error"}},
    summary="Get hourly distribution",
    description="Get hourly distribution of entry/exit events for a specific date."
)
async def get_hourly_stats(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    camera_id: str = Query("default", description="Camera ID to filter by")
):
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
        
        logger.info(f"Fetching hourly stats for date: {date}, camera: {camera_id}")
        
        hourly_data = get_hourly_distribution(date, camera_id)
        
        return [HourlyCount(**row) for row in hourly_data]
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD."
        )
    except Exception as e:
        logger.error(f"Error fetching hourly stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching hourly stats: {str(e)}"
        )


@router.get(
    "/summary",
    summary="Get summary statistics",
    description="Get overall summary statistics across all cameras or for a specific camera."
)
async def get_summary(
    camera_id: Optional[str] = Query(None, description="Camera ID (optional)")
):
    try:
        target_camera = camera_id or "default"
        logger.info(f"Fetching summary for camera: {target_camera}")
        
        # Get total counts
        total_stats = get_total_counts(target_camera)
        
        # Get today's counts
        today = datetime.now().strftime("%Y-%m-%d")
        today_stats = get_daily_counts(today, target_camera)
        
        return {
            "success": True,
            "camera_id": target_camera,
            "total_entry": total_stats['total_entry'],
            "total_exit": total_stats['total_exit'],
            "net_count": total_stats['net_count'],
            "today_entry": today_stats['entry_count'],
            "today_exit": today_stats['exit_count'],
            "today_net": today_stats['net_count']
        }
        
    except Exception as e:
        logger.error(f"Error fetching summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching summary: {str(e)}"
        )
