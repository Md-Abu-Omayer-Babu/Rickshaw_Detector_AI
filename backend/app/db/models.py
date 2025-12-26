"""
Database models and Pydantic schemas.
Defines data structures for API requests and responses.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class DetectionRecord(BaseModel):
    """Schema for detection records in the database."""
    id: int
    file_type: str = Field(..., description="Type of file: 'image' or 'video'")
    file_name: str = Field(..., description="Name of the processed file")
    rickshaw_count: int = Field(..., ge=0, description="Number of rickshaws detected")
    created_at: str = Field(..., description="Timestamp of detection")
    
    class Config:
        from_attributes = True


class RickshawLogRecord(BaseModel):
    """Schema for rickshaw entry/exit log records."""
    id: int
    event_type: str = Field(..., description="Event type: 'entry' or 'exit'")
    camera_id: str = Field(default="default", description="Camera identifier")
    rickshaw_id: Optional[str] = Field(None, description="Tracking ID of rickshaw")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")
    timestamp: str = Field(..., description="Event timestamp")
    frame_number: Optional[int] = Field(None, description="Frame number in video")
    bounding_box: Optional[str] = Field(None, description="Bounding box coordinates")
    crossing_line: Optional[str] = Field(None, description="Line that was crossed")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        from_attributes = True


class ImageDetectionResponse(BaseModel):
    """Response schema for image detection endpoint."""
    success: bool = True
    file_name: str = Field(..., description="Name of the output file")
    rickshaw_count: int = Field(..., ge=0, description="Number of rickshaws detected")
    output_url: str = Field(..., description="URL to access the processed image")
    message: str = "Image processed successfully"


class VideoDetectionResponse(BaseModel):
    """Response schema for video detection endpoint."""
    success: bool = True
    file_name: str = Field(..., description="Name of the output file")
    rickshaw_count: int = Field(..., ge=0, description="Maximum number of rickshaws detected in any frame")
    total_entry: int = Field(default=0, description="Total entry count")
    total_exit: int = Field(default=0, description="Total exit count")
    net_count: int = Field(default=0, description="Net count (entry - exit)")
    output_url: str = Field(..., description="URL to access the processed video")
    message: str = "Video processed successfully"


class CCTVStreamRequest(BaseModel):
    """Request schema for CCTV stream detection."""
    camera_id: str = Field(..., description="Unique camera identifier")
    rtsp_url: str = Field(..., description="RTSP stream URL")
    duration: Optional[int] = Field(60, description="Duration to process in seconds")
    camera_name: Optional[str] = Field("Camera", description="Human-readable camera name")


class CCTVStreamResponse(BaseModel):
    """Response schema for CCTV stream detection."""
    success: bool = True
    camera_id: str = Field(..., description="Camera identifier")
    total_entry: int = Field(..., ge=0, description="Total entry count")
    total_exit: int = Field(..., ge=0, description="Total exit count")
    net_count: int = Field(..., description="Net count (entry - exit)")
    frames_processed: int = Field(..., ge=0, description="Number of frames processed")
    duration: float = Field(..., description="Processing duration in seconds")
    message: str = "Stream processed successfully"


class HistoryResponse(BaseModel):
    """Response schema for history endpoint."""
    success: bool = True
    total_records: int = Field(..., ge=0, description="Total number of detection records")
    detections: List[DetectionRecord] = Field(..., description="List of all detection records")


class RickshawLogsResponse(BaseModel):
    """Response schema for rickshaw logs endpoint."""
    success: bool = True
    total_records: int = Field(..., ge=0, description="Total number of log records")
    logs: List[RickshawLogRecord] = Field(..., description="List of rickshaw event logs")


class DailyCounts(BaseModel):
    """Schema for daily entry/exit counts."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    entry_count: int = Field(..., ge=0, description="Total entry count")
    exit_count: int = Field(..., ge=0, description="Total exit count")
    net_count: int = Field(..., description="Net count (entry - exit)")


class HourlyCount(BaseModel):
    """Schema for hourly distribution."""
    hour: str = Field(..., description="Hour (00-23)")
    event_type: str = Field(..., description="Event type: 'entry' or 'exit'")
    count: int = Field(..., ge=0, description="Count for this hour")


class PeakHourInfo(BaseModel):
    """Schema for peak hour information."""
    hour: int = Field(..., ge=0, le=23, description="Peak hour (0-23)")
    entry_count: int = Field(..., ge=0, description="Entry count during peak hour")
    exit_count: int = Field(..., ge=0, description="Exit count during peak hour")
    total_count: int = Field(..., ge=0, description="Total count during peak hour")


class AnalyticsDashboard(BaseModel):
    """Response schema for analytics dashboard."""
    success: bool = True
    total_entry: int = Field(..., ge=0, description="Total entry count (all time)")
    total_exit: int = Field(..., ge=0, description="Total exit count (all time)")
    net_count: int = Field(..., description="Net count (all time)")
    today_entry: int = Field(..., ge=0, description="Today's entry count")
    today_exit: int = Field(..., ge=0, description="Today's exit count")
    today_net: int = Field(..., description="Today's net count")
    hourly_distribution: List[HourlyCount] = Field(..., description="Hourly distribution for today")
    peak_hour: Optional[PeakHourInfo] = Field(None, description="Peak hour information")
    daily_trend: List[DailyCounts] = Field(..., description="Daily trend (last 7 days)")


class ExportRequest(BaseModel):
    """Request schema for exporting data."""
    format: str = Field(..., description="Export format: 'csv' or 'json'")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    event_type: Optional[str] = Field(None, description="Filter by event type")
    camera_id: Optional[str] = Field(None, description="Filter by camera ID")


class ErrorResponse(BaseModel):
    """Generic error response schema."""
    success: bool = False
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
