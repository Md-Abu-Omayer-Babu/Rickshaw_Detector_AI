"""
Database models and Pydantic schemas.
Defines data structures for API requests and responses.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DetectionRecord(BaseModel):
    """Schema for detection records in the database."""
    id: int
    file_type: str = Field(..., description="Type of file: 'image' or 'video'")
    file_name: str = Field(..., description="Name of the processed file")
    rickshaw_count: int = Field(..., ge=0, description="Number of rickshaws detected")
    created_at: str = Field(..., description="Timestamp of detection")
    
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
    output_url: str = Field(..., description="URL to access the processed video")
    message: str = "Video processed successfully"


class HistoryResponse(BaseModel):
    """Response schema for history endpoint."""
    success: bool = True
    total_records: int = Field(..., ge=0, description="Total number of detection records")
    detections: list[DetectionRecord] = Field(..., description="List of all detection records")


class ErrorResponse(BaseModel):
    """Generic error response schema."""
    success: bool = False
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
