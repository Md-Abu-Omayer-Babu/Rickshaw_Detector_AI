# Live Video Preview Implementation Summary

## Overview
Implemented LIVE PREVIEW for uploaded video processing using MJPEG streaming. Users can now see processed frames (with bounding boxes, entry-exit line, and counts) in real-time during video processing.

## Architecture

### Backend Changes

#### 1. Video Job Manager (`backend/app/services/video_job_manager.py`)
- **New File**: Manages in-memory job state for all video processing jobs
- **Key Features**:
  - Stores latest processed frame for each job
  - Tracks progress (percentage, frames processed)
  - Thread-safe access with locks
  - Automatic cleanup of old jobs (30 minutes after completion)
  - Job states: "processing", "completed", "failed"

#### 2. Video Service Enhancement (`backend/app/services/video_service.py`)
- **Added Method**: `process_video_with_live_preview()`
  - Processes video in background thread
  - Updates job manager with every processed frame (for streaming)
  - Maintains existing detection and counting logic
  - Original `process_video()` method preserved for backward compatibility

#### 3. Video Detection Routes (`backend/app/routes/detect_video.py`)
- **New Endpoint**: `POST /api/detect/video/async`
  - Accepts video upload
  - Starts background processing immediately
  - Returns `job_id` for tracking
- **New Endpoint**: `GET /api/detect/video/status/{job_id}`
  - Check job status and progress
  - Returns final results when completed

#### 4. MJPEG Streaming Route (`backend/app/routes/stream_video.py`)
- **New File & Endpoint**: `GET /api/stream/video/{job_id}`
  - Streams latest processed frame as MJPEG (Motion JPEG)
  - Multipart response format for continuous frame delivery
  - Works with standard `<img>` tag in browsers
  - Automatically closes stream when job completes/fails
  - ~10 FPS streaming rate (configurable via sleep duration)

#### 5. Main App Registration (`backend/app/main.py`)
- Registered `stream_video` router in FastAPI app

### Frontend Changes

#### 1. API Client (`frontend/src/api/client.js`)
- **New Function**: `detectVideoAsync()` - Calls async video endpoint
- **New Function**: `getJobStatus()` - Polls job status
- **New Function**: `getVideoStreamUrl()` - Generates MJPEG stream URL

#### 2. Video Detection Page (`frontend/src/pages/VideoDetection.jsx`)
- **Live Preview Display**:
  - Uses `<img src="/api/stream/video/{job_id}">` for MJPEG stream
  - Shows processing progress bar with percentage
  - Displays frame count progress
  - Auto-polls job status every 2 seconds
  - Transitions to final result when complete
- **Graceful Error Handling**:
  - Handles stream errors
  - Shows error messages from backend
  - Cleans up intervals on unmount

## How It Works

### Flow Diagram
```
User Upload Video
       ↓
POST /api/detect/video/async
       ↓
Backend: Generate job_id, start background thread
       ↓
Return job_id immediately ← Frontend receives job_id
       ↓
Frontend: Show <img src="/api/stream/video/{job_id}">
       ↓
Backend Thread: Process frames
       ↓
For each frame:
  - Run YOLO detection
  - Draw bounding boxes, line, counts
  - Update job_manager.latest_frame ← MJPEG endpoint reads this
       ↓
MJPEG Stream: Continuously yield latest frame as JPEG
       ↓
Frontend: Browser displays frames in <img> tag (live preview)
       ↓
Frontend: Poll /api/detect/video/status/{job_id} every 2s
       ↓
When status === "completed":
  - Stop polling
  - Hide live preview
  - Show final processed video
```

## Key Technical Decisions

### 1. MJPEG vs WebSocket
- **Chose MJPEG** because:
  - Works with standard HTML `<img>` tag (no custom rendering)
  - Simple HTTP streaming (no WebSocket complexity)
  - Built-in browser support
  - Suitable for one-way video streaming

### 2. Threading vs AsyncIO
- **Chose Threading** because:
  - OpenCV video processing is CPU-bound
  - Simpler implementation for single-user scenario
  - Background thread doesn't block FastAPI event loop
  - Easy to manage with Python's threading module

### 3. In-Memory State vs Database
- **Chose In-Memory** because:
  - Fast access for frame retrieval
  - No database overhead for temporary streaming data
  - Automatic cleanup with garbage collection
  - Single-server deployment assumption

### 4. Frame Update Frequency
- **Update every frame** for smooth preview
  - Can be optimized to every N frames if needed
  - Current implementation: ~10 FPS streaming rate

## Testing the Feature

### Backend Testing
```bash
# 1. Start FastAPI server
cd backend
python run.py

# 2. Test async video upload
curl -X POST http://localhost:8000/api/detect/video/async \
  -F "file=@test_video.mp4" \
  -F "enable_counting=true"

# Response: {"job_id": "...", "message": "..."}

# 3. Test MJPEG stream (open in browser)
http://localhost:8000/api/stream/video/{job_id}

# 4. Test status endpoint
curl http://localhost:8000/api/detect/video/status/{job_id}
```

### Frontend Testing
```bash
# 1. Start frontend dev server
cd frontend
npm run dev

# 2. Navigate to Video Detection page
http://localhost:5173/video

# 3. Upload a video and observe:
#    - Live preview appears immediately
#    - Progress bar updates in real-time
#    - Frame count increments
#    - Final result shown when complete
```

## Performance Considerations

### Current Implementation
- **Single Job at a Time**: Designed for single-user scenario
- **Memory Usage**: Stores latest frame per job (~1-3 MB per job)
- **CPU Usage**: Video processing in background thread (doesn't block API)

### Optimization Opportunities (Future)
1. **Frame Skipping**: Update every 3rd frame instead of every frame
2. **Frame Quality**: Lower JPEG quality for streaming (currently 85%)
3. **Concurrent Jobs**: Add job queue with max concurrent limit
4. **Persistent Storage**: Store frames in Redis for multi-instance deployment

## Error Handling

### Backend
- Invalid job_id → 404 Not Found
- Processing error → Job marked as "failed" with error message
- Stream connection lost → Gracefully closes generator

### Frontend
- Stream error → Image hidden, fallback to loader
- Status poll error → Logged to console, retries continue
- Job failure → Error message displayed to user

## Backward Compatibility

- **Original endpoint preserved**: `POST /api/detect/video` still works
- **Old behavior available**: Synchronous processing without live preview
- **No breaking changes**: Existing frontend code unaffected if not using new feature

## Files Modified/Created

### Backend (New Files)
- `backend/app/services/video_job_manager.py` ✨ NEW
- `backend/app/routes/stream_video.py` ✨ NEW

### Backend (Modified)
- `backend/app/services/video_service.py` - Added `process_video_with_live_preview()`
- `backend/app/routes/detect_video.py` - Added async endpoint and status endpoint
- `backend/app/main.py` - Registered stream_video router

### Frontend (Modified)
- `frontend/src/api/client.js` - Added async video APIs
- `frontend/src/pages/VideoDetection.jsx` - Added live preview UI with MJPEG stream

## Configuration

### Adjustable Parameters

In `video_job_manager.py`:
- Job cleanup interval: `time.sleep(300)` → Every 5 minutes
- Job retention: `age_minutes > 30` → 30 minutes after completion

In `stream_video.py`:
- Streaming FPS: `time.sleep(0.1)` → ~10 FPS (adjust to 0.05 for 20 FPS)
- JPEG quality: `cv2.IMWRITE_JPEG_QUALITY, 85` → 85% quality

In `VideoDetection.jsx`:
- Status poll interval: `setInterval(..., 2000)` → Every 2 seconds

## Security Considerations

### Current Implementation
- ⚠️ No authentication on stream endpoint
- ⚠️ Job IDs are UUIDs (hard to guess but not secure)
- ⚠️ No rate limiting on stream endpoint

### Production Recommendations
1. Add authentication token to stream URL
2. Implement per-IP rate limiting
3. Add job ownership validation
4. Set max concurrent streams per user

## Conclusion

This implementation provides a **production-quality live preview feature** for video processing with:
- ✅ Real-time frame streaming via MJPEG
- ✅ Progress tracking with visual feedback
- ✅ Thread-safe job management
- ✅ Graceful error handling
- ✅ Backward compatibility
- ✅ Clean code with comments

The feature is ready for immediate use and can be further optimized based on actual usage patterns and performance requirements.
