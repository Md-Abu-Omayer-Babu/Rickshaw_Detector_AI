import cv2
import numpy as np
import json
from pathlib import Path
from fastapi import UploadFile
from app.model.detector import YOLODetector
from app.utils.draw_utils import (
    draw_detections, draw_count_overlay, draw_entry_exit_line, 
    draw_entry_exit_counts
)
from app.utils.file_utils import generate_unique_filename, save_upload_file, get_output_url
from app.utils.count_utils import LineCrossingDetector, SimpleTracker
from app.db.database import insert_detection, log_rickshaw_event
from app.core.config import settings, logger
from app.services.video_job_manager import get_job_manager


class VideoService:
    def __init__(self, detector: YOLODetector):
        self.detector = detector

    async def process_video(
        self, 
        file: UploadFile,
        enable_counting: bool = True,
        camera_id: str = "default"
    ) -> dict:
        logger.info(f"Starting video processing: {file.filename}, counting={enable_counting}")

        output_filename = generate_unique_filename(file.filename)
        temp_input_path = settings.videos_output_dir / f"temp_input_{output_filename}"
        output_path = settings.videos_output_dir / output_filename

        try:
            # Save uploaded file temporarily
            await save_upload_file(file, temp_input_path)
            logger.info(f"Video saved temporarily: {temp_input_path}")

            # Open video file
            cap = cv2.VideoCapture(str(temp_input_path))
            if not cap.isOpened():
                raise ValueError("Failed to open video file")

            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            logger.info(f"Video properties: {width}x{height} @ {fps}fps, {total_frames} frames")

            line_detector = SimpleTracker() if not enable_counting else LineCrossingDetector(
                line_start=settings.entry_line_start,
                line_end=settings.entry_line_end,
                frame_width=width,
                frame_height=height,
                use_percentage=True
            ) if enable_counting else None
            tracker = SimpleTracker() if enable_counting else None

            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

            max_rickshaw_count = 0
            frame_count = 0
            total_entry = 0
            total_exit = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1  # ✅ increment frame counter

                # Run detection
                detection_result = self.detector.detect(frame)
                frame_rickshaw_count = self.detector.count_rickshaws(detection_result)
                max_rickshaw_count = max(max_rickshaw_count, frame_rickshaw_count)

                annotated_frame = draw_detections(frame, detection_result, self.detector)

                if enable_counting and line_detector and tracker and len(detection_result) > 0:
                    tracked_objects = tracker.update(detection_result.boxes)
                    for track_id, bbox in tracked_objects.items():
                        event = line_detector.update(
                            object_id=str(track_id),
                            bbox=bbox,
                            frame_number=frame_count
                        )
                        if event:
                            bbox_json = json.dumps(bbox.tolist())
                            confidence = detection_result.confidences[0] if len(detection_result.confidences) > 0 else 0.0
                            log_rickshaw_event(
                                event_type=event,
                                confidence=float(confidence),
                                camera_id=camera_id,
                                rickshaw_id=str(track_id),
                                frame_number=frame_count,
                                bounding_box=bbox_json,
                                crossing_line="entry_line"
                            )

                # Always draw line and counts when counting is enabled
                if enable_counting and line_detector:
                    entry_count, exit_count, net_count = line_detector.get_counts()
                    total_entry = entry_count
                    total_exit = exit_count

                    line_start, line_end = line_detector.get_line_pixels()
                    annotated_frame = draw_entry_exit_line(annotated_frame, line_start, line_end, label="Counting Line")
                    annotated_frame = draw_entry_exit_counts(annotated_frame, entry_count, exit_count, net_count)
                else:
                    annotated_frame = draw_count_overlay(annotated_frame, frame_rickshaw_count)

                out.write(annotated_frame)

            cap.release()
            out.release()

            if temp_input_path.exists():
                temp_input_path.unlink()

            logger.info(f"Video processing complete: {frame_count} frames processed")
            logger.info(f"Max rickshaw count: {max_rickshaw_count}, Entry: {total_entry}, Exit: {total_exit}")

            insert_detection(
                file_type="video",
                file_name=output_filename,
                rickshaw_count=max_rickshaw_count
            )

            output_url = get_output_url(output_filename, "video")

            return {
                "file_name": output_filename,
                "rickshaw_count": max_rickshaw_count,
                "total_entry": total_entry,
                "total_exit": total_exit,
                "net_count": total_entry - total_exit,
                "output_url": output_url,
                "frames_processed": frame_count
            }

        except Exception as e:
            logger.error(f"Error processing video: {str(e)}", exc_info=True)
            if temp_input_path.exists():
                temp_input_path.unlink()
            if output_path.exists():
                output_path.unlink()
            raise e

    def process_video_with_live_preview(
        self,
        job_id: str,
        temp_input_path: Path,
        output_filename: str,
        enable_counting: bool = True,
        camera_id: str = "default"
    ):
        job_manager = get_job_manager()
        output_path = settings.videos_output_dir / output_filename

        try:
            logger.info(f"[Job {job_id}] Starting background video processing")

            cap = cv2.VideoCapture(str(temp_input_path))
            if not cap.isOpened():
                raise ValueError("Failed to open video file")

            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            logger.info(f"[Job {job_id}] Video: {width}x{height} @ {fps}fps, {total_frames} frames")

            job_manager.create_job(job_id, total_frames)

            line_detector = None
            tracker = None
            if enable_counting:
                line_detector = LineCrossingDetector(
                    line_start=settings.entry_line_start,
                    line_end=settings.entry_line_end,
                    frame_width=width,
                    frame_height=height,
                    use_percentage=True
                )
                tracker = SimpleTracker()

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

            max_rickshaw_count = 0
            frame_count = 0
            total_entry = 0
            total_exit = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1  # ✅ increment frame counter

                detection_result = self.detector.detect(frame)
                frame_rickshaw_count = self.detector.count_rickshaws(detection_result)
                max_rickshaw_count = max(max_rickshaw_count, frame_rickshaw_count)

                annotated_frame = draw_detections(frame, detection_result, self.detector)

                if enable_counting and line_detector and tracker and len(detection_result) > 0:
                    tracked_objects = tracker.update(detection_result.boxes)
                    for track_id, bbox in tracked_objects.items():
                        event = line_detector.update(
                            object_id=str(track_id),
                            bbox=bbox,
                            frame_number=frame_count
                        )
                        if event:
                            bbox_json = json.dumps(bbox.tolist())
                            confidence = detection_result.confidences[0] if len(detection_result.confidences) > 0 else 0.0
                            log_rickshaw_event(
                                event_type=event,
                                confidence=float(confidence),
                                camera_id=camera_id,
                                rickshaw_id=str(track_id),
                                frame_number=frame_count,
                                bounding_box=bbox_json,
                                crossing_line="entry_line"
                            )

                # Always draw line and counts when counting is enabled
                if enable_counting and line_detector:
                    entry_count, exit_count, net_count = line_detector.get_counts()
                    total_entry = entry_count
                    total_exit = exit_count

                    line_start, line_end = line_detector.get_line_pixels()
                    annotated_frame = draw_entry_exit_line(annotated_frame, line_start, line_end, label="Counting Line")
                    annotated_frame = draw_entry_exit_counts(annotated_frame, entry_count, exit_count, net_count)
                else:
                    annotated_frame = draw_count_overlay(annotated_frame, frame_rickshaw_count)

                out.write(annotated_frame)

                # Update progress and frame to JobManager
                if frame_count % 10 == 0 or frame_count == total_frames:
                    progress = int((frame_count / total_frames) * 100)
                    progress = min(100, max(1, progress))
                    logger.info(f"[Job {job_id}] Progress: {frame_count}/{total_frames} ({progress}%)")

                # Optional live preview throttling - update_frame also updates progress
                # Always update first frame to start stream immediately
                if settings.preview_update_interval and (frame_count == 1 or frame_count % settings.preview_update_interval == 0):
                    job_manager.update_frame(job_id, annotated_frame, frame_count)

            cap.release()
            out.release()

            if temp_input_path.exists():
                temp_input_path.unlink()

            insert_detection(
                file_type="video",
                file_name=output_filename,
                rickshaw_count=max_rickshaw_count
            )

            output_url = get_output_url(output_filename, "video")

            result = {
                "file_name": output_filename,
                "rickshaw_count": max_rickshaw_count,
                "total_entry": total_entry,
                "total_exit": total_exit,
                "net_count": total_entry - total_exit,
                "output_url": output_url,
                "frames_processed": frame_count
            }

            job_manager.mark_completed(job_id, result)
            logger.info(f"[Job {job_id}] Marked as completed")

        except Exception as e:
            error_msg = f"Error processing video: {str(e)}"
            logger.error(f"[Job {job_id}] {error_msg}", exc_info=True)
            job_manager.mark_failed(job_id, error_msg)

            if temp_input_path.exists():
                temp_input_path.unlink()
            if output_path.exists():
                output_path.unlink()
