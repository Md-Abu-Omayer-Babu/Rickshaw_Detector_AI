"""
File utility functions for handling file uploads and storage.
"""
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename using UUID while preserving the extension.
    
    Args:
        original_filename: Original uploaded filename
        
    Returns:
        str: Unique filename with original extension
    """
    # Get file extension
    extension = Path(original_filename).suffix.lower()
    
    # Generate UUID-based filename
    unique_name = f"{uuid.uuid4()}{extension}"
    
    return unique_name


def validate_image_file(file: UploadFile) -> None:
    """
    Validate uploaded image file.
    
    Args:
        file: Uploaded file
        
    Raises:
        HTTPException: If file is invalid
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    extension = Path(file.filename).suffix.lower()
    if extension not in settings.allowed_image_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image format. Allowed formats: {', '.join(settings.allowed_image_extensions)}"
        )
    
    # Check content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Must be an image."
        )


def validate_video_file(file: UploadFile) -> None:
    """
    Validate uploaded video file.
    
    Args:
        file: Uploaded file
        
    Raises:
        HTTPException: If file is invalid
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    extension = Path(file.filename).suffix.lower()
    if extension not in settings.allowed_video_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid video format. Allowed formats: {', '.join(settings.allowed_video_extensions)}"
        )
    
    # Check content type
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Must be a video."
        )


async def save_upload_file(file: UploadFile, destination_path: Path) -> None:
    """
    Save uploaded file to disk.
    
    Args:
        file: Uploaded file
        destination_path: Path where file should be saved
    """
    # Create parent directories if they don't exist
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read and write file in chunks to handle large files
    chunk_size = 1024 * 1024  # 1 MB chunks
    
    with open(destination_path, "wb") as f:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)


def get_output_url(filename: str, file_type: str) -> str:
    """
    Generate URL for accessing output files.
    
    Args:
        filename: Name of the output file
        file_type: Type of file ('image' or 'video')
        
    Returns:
        str: URL path to access the file
    """
    return f"/outputs/{file_type}s/{filename}"
