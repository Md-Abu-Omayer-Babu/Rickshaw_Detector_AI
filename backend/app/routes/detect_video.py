import uuid
import threading
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from app.db.models import VideoDetectionResponse, ErrorResponse
from app.services.video_service import VideoService
from app.services.video_job_manager import get_job_manager
from app.core.startup import get_detector
from app.utils.file_utils import validate_video_file, generate_unique_filename, save_upload_file
from app.core.config import settings, logger


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
    description="Upload a video file to detect and count rickshaws frame by frame with entry/exit counting. Returns annotated video with bounding boxes and counts."
)
async def detect_video(
    file: UploadFile = File(..., description="Video file to process"),
    enable_counting: bool = Query(True, description="Enable entry/exit counting"),
    camera_id: str = Query("default", description="Camera identifier for logging")
):
    try:
        logger.info(f"Video detection request: {file.filename}, counting={enable_counting}")
        
        # Validate file
        validate_video_file(file)
        
        # Get detector instance
        detector = get_detector()
        
        # Create video service
        video_service = VideoService(detector)
        
        # Process video
        result = await video_service.process_video(
            file=file,
            enable_counting=enable_counting,
            camera_id=camera_id
        )
        
        logger.info(f"Video processing complete: {result}")
        
        return VideoDetectionResponse(
            file_name=result["file_name"],
            rickshaw_count=result["rickshaw_count"],
            total_entry=result["total_entry"],
            total_exit=result["total_exit"],
            net_count=result["net_count"],
            output_url=result["output_url"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )


@router.post(
    "/video/async",
    summary="Start video processing with live preview (async)",
    description="Upload a video and start processing in background. Returns job_id immediately for live preview streaming."
)
async def detect_video_async(
    file: UploadFile = File(..., description="Video file to process"),
    enable_counting: bool = Query(True, description="Enable entry/exit counting"),
    camera_id: str = Query("default", description="Camera identifier for logging")
):
    try:
        logger.info(f"Async video detection request: {file.filename}")
        
        # Validate file
        validate_video_file(file)
        
        # Generate job ID and filenames
        job_id = str(uuid.uuid4())
        output_filename = generate_unique_filename(file.filename)
        temp_input_path = settings.videos_output_dir / f"temp_input_{output_filename}"
        
        # Save uploaded file temporarily
        await save_upload_file(file, temp_input_path)
        logger.info(f"[Job {job_id}] Video saved temporarily: {temp_input_path}")
        
        # Get detector instance
        detector = get_detector()
        
        # Create video service
        video_service = VideoService(detector)
        
        # *** Start processing in background thread ***
        processing_thread = threading.Thread(
            target=video_service.process_video_with_live_preview,
            args=(job_id, temp_input_path, output_filename, enable_counting, camera_id),
            daemon=True
        )
        processing_thread.start()
        
        logger.info(f"[Job {job_id}] Processing started in background thread")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Video processing started. Use /api/stream/video/{job_id} for live preview."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting async video processing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error starting video processing: {str(e)}"
        )


@router.get(
    "/video/status/{job_id}",
    summary="Get video processing job status",
    description="Check the status and progress of a video processing job."
)
async def get_job_status(job_id: str):
    try:
        job_manager = get_job_manager()
        job = job_manager.get_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job not found: {job_id}"
            )
        
        response = {
            "job_id": job_id,
            "status": job.status,
            "progress": job.progress,
            "processed_frames": job.processed_frames,
            "total_frames": job.total_frames,
            "entry_count": job.total_entry,
            "exit_count": job.total_exit
        }
        
        # Include results if completed
        if job.status == "completed":
            response["result"] = {
                "file_name": job.output_filename,
                "rickshaw_count": job.rickshaw_count,
                "total_entry": job.total_entry,
                "total_exit": job.total_exit,
                "net_count": job.net_count,
                "output_url": job.output_url
            }
        
        # Include error if failed
        if job.status == "failed":
            response["error"] = job.error_message
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )


@router.post(
    "/video/pause/{job_id}",
    summary="Pause video processing",
    description="Pause a running video processing job."
)
async def pause_job(job_id: str):
    try:
        job_manager = get_job_manager()
        success = job_manager.pause_job(job_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot pause job: {job_id}. Job may not exist or not in processing state."
            )
        
        return {"success": True, "message": f"Job {job_id} paused"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/video/resume/{job_id}",
    summary="Resume video processing",
    description="Resume a paused video processing job."
)
async def resume_job(job_id: str):
    try:
        job_manager = get_job_manager()
        success = job_manager.resume_job(job_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot resume job: {job_id}. Job may not exist or not in paused state."
            )
        
        return {"success": True, "message": f"Job {job_id} resumed"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/video/stop/{job_id}",
    summary="Stop video processing",
    description="Stop a running or paused video processing job."
)
async def stop_job(job_id: str):
    try:
        job_manager = get_job_manager()
        success = job_manager.stop_job(job_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot stop job: {job_id}. Job may not exist or already completed."
            )
        
        return {"success": True, "message": f"Job {job_id} stopped"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
