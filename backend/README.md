# Smart Rickshaw Entry-Exit Monitoring System - Backend

A production-ready FastAPI backend for real-time rickshaw detection, tracking, and entry-exit counting using YOLO-based machine learning.

## Features

### 🎯 Core Detection
- **Image Detection**: Upload and analyze single images for rickshaw detection
- **Video Processing**: Frame-by-frame detection with annotated output
- **CCTV/RTSP Streams**: Real-time detection from live camera feeds

### 📊 Entry-Exit Monitoring
- **Line Crossing Detection**: Virtual line-based entry/exit counting
- **Object Tracking**: Tracks rickshaws across frames to prevent duplicate counting
- **Multi-Camera Support**: Process multiple camera streams concurrently
- **Event Logging**: Detailed logs of every entry/exit event with timestamps and bounding boxes

### 📈 Analytics & Reporting
- **Real-time Dashboard**: Comprehensive statistics with trends and peak hours
- **Daily Reports**: Day-by-day entry/exit counts
- **Hourly Distribution**: Hour-by-hour breakdown of traffic patterns
- **Peak Hour Analysis**: Automatic detection of busiest periods
- **7-Day Trends**: Historical trend visualization

### 💾 Data Export
- **CSV Export**: Export logs and analytics as CSV files
- **JSON Export**: Export data in JSON format for integration
- **Flexible Filtering**: Filter by date range, event type, camera ID

### 🚀 Production-Ready
- **Rotating Logs**: Automatic log file rotation (10 MB, 5 backups)
- **Error Handling**: Comprehensive error handling and recovery
- **Database Optimization**: Indexes for fast queries
- **Auto-Reconnect**: Automatic CCTV stream reconnection
- **Interactive API Docs**: Swagger UI and ReDoc

## Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **Ultralytics YOLO**: State-of-the-art object detection
- **OpenCV**: Video and image processing
- **SQLite3**: Lightweight database with 4 tables
- **Python 3.10+**: Required Python version
- **Pydantic**: Data validation with 20+ schemas

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   ├── config.py             # Application settings (90+ config options)
│   │   └── startup.py            # Startup/shutdown lifecycle
│   ├── model/
│   │   └── detector.py           # YOLO detector wrapper
│   ├── routes/                    # API endpoints (7 route files)
│   │   ├── detect_image.py       # POST /api/detect/image
│   │   ├── detect_video.py       # POST /api/detect/video
│   │   ├── detect_cctv.py        # POST /api/cctv/stream
│   │   ├── history.py            # GET /api/history
│   │   ├── logs.py               # GET /api/logs
│   │   ├── analytics.py          # GET /api/analytics/*
│   │   └── export.py             # GET /api/export/*
│   ├── services/                  # Business logic
│   │   ├── inference_service.py  # Image detection service
│   │   ├── video_service.py      # Video processing with counting
│   │   └── cctv_service.py       # CCTV stream service
│   ├── db/
│   │   ├── database.py           # Database operations (15+ functions)
│   │   └── models.py             # Pydantic schemas (20+ models)
│   ├── utils/
│   │   ├── count_utils.py        # Line crossing & tracking (350+ lines)
│   │   ├── draw_utils.py         # Visualization utilities
│   │   └── file_utils.py         # File validation
│   └── outputs/                   # Generated outputs
│       ├── images/               # Processed images
│       └── videos/               # Processed videos
├── database/                      # SQLite database files
│   └── detections.db             # Main database (4 tables)
├── logs/                          # Application logs
│   └── app.log                   # Rotating log file
├── uploads/                       # Temporary upload storage
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── API_GUIDE.md                  # Quick reference guide
└── REFACTORING_SUMMARY.md        # Technical summary
```

## Database Schema

### Tables

1. **detections** - Basic detection results
   ```sql
   CREATE TABLE detections (
       id INTEGER PRIMARY KEY,
       timestamp DATETIME,
       file_name TEXT,
       file_type TEXT,
       rickshaw_count INTEGER
   );
   ```

2. **rickshaw_logs** - Entry/exit event logs
   ```sql
   CREATE TABLE rickshaw_logs (
       id INTEGER PRIMARY KEY,
       timestamp DATETIME,
       event_type TEXT,         -- 'entry' or 'exit'
       camera_id TEXT,
       confidence REAL,
       bbox_x1 REAL, bbox_y1 REAL,
       bbox_x2 REAL, bbox_y2 REAL
   );
   ```

3. **analytics_summary** - Cached daily aggregations
   ```sql
   CREATE TABLE analytics_summary (
       id INTEGER PRIMARY KEY,
       date DATE UNIQUE,
       entry_count INTEGER,
       exit_count INTEGER,
       net_count INTEGER
   );
   ```

4. **camera_streams** - CCTV camera configuration
   ```sql
   CREATE TABLE camera_streams (
       id INTEGER PRIMARY KEY,
       camera_id TEXT UNIQUE,
       rtsp_url TEXT,
       status TEXT,
       last_active DATETIME
   );
   ```

## Installation

### Prerequisites

- Python 3.10 or higher
- YOLO model file (`best.pt`) in `trained_model/` directory (one level up from backend)
- pip package manager

### Setup Steps

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify model file**:
   Ensure `best.pt` exists in `../trained_model/best.pt`

5. **Configure settings** (optional):
   Edit `app/core/config.py` to customize entry/exit line position, CCTV settings, etc.

## Running the Application

### Quick Start

```bash
# From backend directory
python app/main.py
```

### Using Uvicorn (Development)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API Root**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Detection APIs

#### 1. Image Detection

**POST** `/api/detect/image`

Upload an image to detect rickshaws.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/detect/image" \
  -F "file=@test_image.jpg"
```

**Response**:
```json
{
  "file_name": "output_20251226_120000.jpg",
  "rickshaw_count": 5,
  "output_url": "/outputs/output_20251226_120000.jpg"
}
```

**Supported formats**: JPG, JPEG, PNG, BMP, WEBP

---

#### 2. Video Detection with Entry/Exit Counting

**POST** `/api/detect/video`

Process video with frame-by-frame detection and entry/exit counting.

**Parameters**:
- `file` (required): Video file
- `enable_counting` (optional, default: true): Enable entry/exit counting
- `camera_id` (optional, default: "default"): Camera identifier

**Request**:
```bash
curl -X POST "http://localhost:8000/api/detect/video?enable_counting=true&camera_id=test_cam" \
  -F "file=@test_video.mp4"
```

**Response**:
```json
{
  "file_name": "output_20251226_120000.mp4",
  "rickshaw_count": 12,
  "total_entry": 15,
  "total_exit": 8,
  "net_count": 7,
  "output_url": "/outputs/output_20251226_120000.mp4"
}
```

**Supported formats**: MP4, AVI, MOV, MKV

---

#### 3. CCTV/RTSP Stream Processing

**POST** `/api/cctv/stream`

Process live RTSP stream for specified duration.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/cctv/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "rtsp_url": "rtsp://192.168.1.100:554/stream1",
    "camera_id": "entrance_camera",
    "duration": 300,
    "save_video": true
  }'
```

**Response**:
```json
{
  "camera_id": "entrance_camera",
  "duration": 300,
  "frames_processed": 9000,
  "total_entry": 45,
  "total_exit": 38,
  "net_count": 7,
  "output_url": "/outputs/cctv_entrance_camera_20251226_120000.mp4",
  "status": "completed"
}
```

---

#### 4. Test CCTV Connection

**POST** `/api/cctv/stream/test`

Test RTSP stream connectivity and get stream properties.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/cctv/stream/test" \
  -H "Content-Type: application/json" \
  -d '{"rtsp_url": "rtsp://192.168.1.100:554/stream1"}'
```

**Response**:
```json
{
  "success": true,
  "rtsp_url": "rtsp://192.168.1.100:554/stream1",
  "width": 1920,
  "height": 1080,
  "fps": 30.0,
  "message": "Stream connection successful"
}
```

---

### Data Access APIs

#### 5. Detection History

**GET** `/api/history`

Retrieve detection history with pagination.

**Parameters**:
- `skip` (default: 0): Records to skip
- `limit` (default: 10): Max records to return

**Request**:
```bash
curl "http://localhost:8000/api/history?skip=0&limit=10"
```

**Response**:
```json
{
  "total": 150,
  "records": [
    {
      "id": 1,
      "timestamp": "2025-12-26T12:00:00",
      "file_name": "video1.mp4",
      "file_type": "video",
      "rickshaw_count": 8
    }
  ]
}
```

---

#### 6. Event Logs

**GET** `/api/logs`

Get rickshaw entry/exit event logs with filtering.

**Parameters**:
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `event_type` (optional): "entry" or "exit"
- `camera_id` (optional): Camera identifier
- `limit` (default: 100): Max records
- `offset` (default: 0): Skip records

**Request**:
```bash
curl "http://localhost:8000/api/logs?start_date=2025-12-01&event_type=entry&limit=50"
```

**Response**:
```json
{
  "total": 150,
  "count": 50,
  "offset": 0,
  "limit": 50,
  "logs": [
    {
      "id": 1,
      "timestamp": "2025-12-26T12:00:00",
      "event_type": "entry",
      "camera_id": "camera_01",
      "confidence": 0.95,
      "bbox_x1": 100,
      "bbox_y1": 200,
      "bbox_x2": 300,
      "bbox_y2": 400
    }
  ],
  "filters_applied": {
    "start_date": "2025-12-01",
    "event_type": "entry"
  }
}
```

---

#### 7. Log Statistics

**GET** `/api/logs/stats`

Get quick statistics about logged events.

**Request**:
```bash
curl "http://localhost:8000/api/logs/stats"
```

**Response**:
```json
{
  "total_events": 1000,
  "entry_count": 580,
  "exit_count": 420,
  "net_count": 160,
  "cameras": ["camera_01", "camera_02"],
  "camera_count": 2
}
```

---

### Analytics APIs

#### 8. Analytics Dashboard

**GET** `/api/analytics/dashboard`

Comprehensive analytics dashboard with trends and peak hours.

**Request**:
```bash
curl "http://localhost:8000/api/analytics/dashboard"
```

**Response**:
```json
{
  "total_entry": 580,
  "total_exit": 420,
  "net_count": 160,
  "today_entry": 45,
  "today_exit": 38,
  "today_net": 7,
  "peak_hour": {
    "hour": 14,
    "entry_count": 25,
    "exit_count": 18
  },
  "last_7_days": [
    {
      "date": "2025-12-26",
      "entry_count": 80,
      "exit_count": 60,
      "net_count": 20
    }
  ],
  "active_cameras": 2
}
```

---

#### 9. Daily Analytics

**GET** `/api/analytics/daily`

Get daily counts for date range.

**Parameters**:
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Request**:
```bash
curl "http://localhost:8000/api/analytics/daily?start_date=2025-12-01&end_date=2025-12-26"
```

---

#### 10. Hourly Analytics

**GET** `/api/analytics/hourly`

Get hourly distribution for a specific date.

**Parameters**:
- `date` (required): Target date (YYYY-MM-DD)

**Request**:
```bash
curl "http://localhost:8000/api/analytics/hourly?date=2025-12-26"
```

---

#### 11. Analytics Summary

**GET** `/api/analytics/summary`

Quick summary of key metrics.

**Request**:
```bash
curl "http://localhost:8000/api/analytics/summary"
```

---

### Export APIs

#### 12. Export Logs

**GET** `/api/export/logs`

Export logs as CSV or JSON.

**Parameters**:
- `format`: "csv" or "json" (default: csv)
- `start_date`, `end_date`, `event_type`, `camera_id`: Filters
- `limit` (default: 10000): Max records

**Request**:
```bash
# Export as CSV
curl "http://localhost:8000/api/export/logs?format=csv&start_date=2025-12-01" -o logs.csv

# Export as JSON
curl "http://localhost:8000/api/export/logs?format=json" -o logs.json
```

---

#### 13. Export Analytics

**GET** `/api/export/analytics`

Export analytics summary as CSV or JSON.

**Parameters**:
- `format`: "csv" or "json" (default: csv)
- `days` (default: 30): Number of past days

**Request**:
```bash
curl "http://localhost:8000/api/export/analytics?format=csv&days=30" -o analytics.csv
```

## Configuration

### Key Settings in `app/core/config.py`

#### Entry/Exit Line Position
Configure the virtual counting line (percentage-based coordinates):
```python
# Line coordinates as percentage of frame dimensions
ENTRY_EXIT_LINE_X1_PERCENT = 0.3  # Start X (30% from left)
ENTRY_EXIT_LINE_Y1_PERCENT = 0.0  # Start Y (top of frame)
ENTRY_EXIT_LINE_X2_PERCENT = 0.3  # End X (30% from left)
ENTRY_EXIT_LINE_Y2_PERCENT = 1.0  # End Y (bottom of frame)
```

#### Detection Settings
```python
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for detections
IOU_THRESHOLD = 0.4         # IoU threshold for NMS
YOLO_DEVICE = "cpu"         # Use "cuda" for GPU
```

#### CCTV Settings
```python
MAX_CONCURRENT_STREAMS = 4      # Max simultaneous streams
CCTV_RECONNECT_ATTEMPTS = 3     # Reconnection attempts
CCTV_RECONNECT_DELAY = 5        # Delay between reconnects (seconds)
CCTV_FRAME_SKIP = 2            # Process every Nth frame
CCTV_TARGET_FPS = 30           # Target FPS for processing
```

#### Logging Configuration
```python
LOG_LEVEL = "INFO"              # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/app.log"       # Log file path
LOG_MAX_BYTES = 10485760        # 10 MB max size
LOG_BACKUP_COUNT = 5            # Keep 5 backup files
```

#### CORS Settings
```python
CORS_ORIGINS = ["*"]            # Allowed origins
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
```

## Entry-Exit Counting Algorithm

The system uses a sophisticated line-crossing detection algorithm:

### How It Works

1. **Virtual Line Definition**
   - Configurable line placed in the frame using percentage-based coordinates
   - Resolution-independent (works with any video size)

2. **Object Detection**
   - YOLO detects rickshaws in each frame
   - Returns bounding boxes and confidence scores

3. **Object Tracking**
   - `SimpleTracker` maintains object IDs across frames
   - Uses IoU (Intersection over Union) matching
   - Prevents duplicate counting

4. **Line Crossing Detection**
   - Tracks object centroids frame-by-frame
   - Uses CCW (Counter-Clockwise) test for line intersection
   - Determines direction (entry vs exit) based on side-of-line calculation

5. **Event Logging**
   - Each crossing logged to database with:
     - Timestamp
     - Event type (entry/exit)
     - Camera ID
     - Confidence score
     - Bounding box coordinates

### Key Classes

- **LineCrossingDetector** (`app/utils/count_utils.py`)
  - Implements line crossing logic
  - CCW test for intersection detection
  - Side-of-line calculation for direction

- **SimpleTracker** (`app/utils/count_utils.py`)
  - IoU-based object tracking
  - Automatic ID assignment
  - Lost track cleanup

- **CCTVStreamProcessor** (`app/services/cctv_service.py`)
  - Single stream management
  - Auto-reconnect logic
  - FPS limiting

- **CCTVService** (`app/services/cctv_service.py`)
  - Multi-stream management
  - Concurrent processing
  - Resource management

## Database Management

### Viewing Data

```bash
# Open database
sqlite3 database/detections.db

# List all tables
.tables

# View recent logs
SELECT * FROM rickshaw_logs ORDER BY timestamp DESC LIMIT 10;

# Get today's counts
SELECT 
  SUM(CASE WHEN event_type='entry' THEN 1 ELSE 0 END) as entries,
  SUM(CASE WHEN event_type='exit' THEN 1 ELSE 0 END) as exits
FROM rickshaw_logs 
WHERE DATE(timestamp) = DATE('now');

# Get daily summary
SELECT date, entry_count, exit_count, net_count 
FROM analytics_summary 
ORDER BY date DESC;

# Camera statistics
SELECT camera_id, COUNT(*) as events
FROM rickshaw_logs 
GROUP BY camera_id;
```

### Backup Database

```bash
# Create backup
sqlite3 database/detections.db ".backup 'backup_20251226.db'"

# Restore from backup
sqlite3 database/detections.db ".restore 'backup_20251226.db'"
```

## Logging

Application logs are stored in `logs/app.log` with automatic rotation.

### Log Format
```
[2025-12-26 12:00:00] [INFO] [module_name] Log message here
```

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages with stack traces

### View Logs

```bash
# Windows PowerShell
Get-Content logs/app.log -Wait

# Linux/Mac
tail -f logs/app.log

# Search for errors
Select-String -Pattern "ERROR" -Path logs/app.log
```

## Error Handling

### HTTP Status Codes
- `200`: Success
- `400`: Bad request (invalid file format, invalid parameters)
- `404`: Not found (no data matching filters)
- `422`: Validation error
- `500`: Internal server error

### Error Response Format
```json
{
  "detail": "Error message with specific information"
}
```

## Testing with curl

### Test All Endpoints

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Image detection
curl -X POST http://localhost:8000/api/detect/image \
  -F "file=@test_image.jpg"

# 3. Video with counting
curl -X POST "http://localhost:8000/api/detect/video?enable_counting=true&camera_id=test" \
  -F "file=@test_video.mp4"

# 4. Test CCTV connection
curl -X POST http://localhost:8000/api/cctv/stream/test \
  -H "Content-Type: application/json" \
  -d '{"rtsp_url": "rtsp://camera-ip:554/stream"}'

# 5. View history
curl http://localhost:8000/api/history?limit=5

# 6. View logs
curl "http://localhost:8000/api/logs?start_date=2025-12-01&limit=10"

# 7. Analytics dashboard
curl http://localhost:8000/api/analytics/dashboard

# 8. Export logs as CSV
curl "http://localhost:8000/api/export/logs?format=csv" -o logs.csv
```

## CCTV Stream Testing

### Common RTSP URL Formats

```
Generic:     rtsp://ip:554/stream
Hikvision:   rtsp://username:password@ip:554/Streaming/Channels/101
Dahua:       rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0
TP-Link:     rtsp://username:password@ip:554/stream1
Axis:        rtsp://ip:554/axis-media/media.amp
```

### Test with VLC First

```bash
# Test if stream is accessible
vlc rtsp://your-camera-ip:554/stream
```

### Test via API

```bash
curl -X POST http://localhost:8000/api/cctv/stream/test \
  -H "Content-Type: application/json" \
  -d '{
    "rtsp_url": "rtsp://192.168.1.100:554/stream1"
  }'
```

## Performance Tips

### Video Processing
1. **Enable GPU**: Set `YOLO_DEVICE = "cuda"` in config if NVIDIA GPU available
2. **Frame Skipping**: Increase `CCTV_FRAME_SKIP` for faster processing (e.g., 3 or 5)
3. **Lower Resolution**: Process lower resolution streams if acceptable
4. **Adjust Confidence**: Higher confidence threshold = faster processing

### CCTV Streams
1. **Limit Concurrent Streams**: Reduce `MAX_CONCURRENT_STREAMS` if experiencing lag
2. **FPS Limiting**: Reduce `CCTV_TARGET_FPS` to decrease CPU usage
3. **Frame Skip**: Increase `CCTV_FRAME_SKIP` to process fewer frames
4. **Use Sub-stream**: Many cameras have main and sub-streams; use sub-stream for monitoring

### Database
1. **Regular Cleanup**: Export and archive old logs periodically
2. **Use Filters**: Always use date filters when querying large datasets
3. **Backup**: Regular database backups to prevent data loss

### General
1. **Production Deployment**: Use multiple workers with Gunicorn
2. **Logging Level**: Use `INFO` or `WARNING` in production (not `DEBUG`)
3. **Resource Monitoring**: Monitor CPU/memory usage during concurrent stream processing

## Troubleshooting

### Model Not Found
```
Error: Cannot find model file at trained_model/best.pt
```
**Solution**: 
- Ensure `best.pt` exists in `trained_model/` directory
- Check the file path in config is correct
- Verify file permissions

### RTSP Connection Failed
```
Error: Failed to connect to RTSP stream
```
**Solutions**:
- Test stream with VLC first: `vlc rtsp://camera-ip:554/stream`
- Verify camera IP address and port
- Check firewall settings (RTSP uses port 554)
- Verify credentials if camera requires authentication
- Check network connectivity to camera
- Use `/api/cctv/stream/test` endpoint to diagnose

### CUDA/GPU Errors
```
Error: CUDA out of memory / CUDA not available
```
**Solutions**:
- Set `YOLO_DEVICE = "cpu"` in config to use CPU instead
- Reduce batch size or concurrent streams
- Update NVIDIA drivers
- Verify PyTorch CUDA installation: `torch.cuda.is_available()`

### Low FPS / Slow Processing
```
Warning: Processing FPS is too low
```
**Solutions**:
- Enable GPU if available
- Increase `CCTV_FRAME_SKIP` (e.g., from 2 to 5)
- Reduce `MAX_CONCURRENT_STREAMS`
- Lower input resolution
- Increase confidence threshold to reduce detections

### Out of Memory
```
Error: System out of memory
```
**Solutions**:
- Reduce `MAX_CONCURRENT_STREAMS`
- Enable `CCTV_FRAME_SKIP` to process fewer frames
- Close other memory-intensive applications
- Use CPU instead of GPU (GPU memory limits)

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port in startup command:
```bash
uvicorn app.main:app --port 8001
```

### Import Errors
```
Error: ModuleNotFoundError
```
**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### Database Locked
```
Error: database is locked
```
**Solution**: 
- Ensure only one instance is running
- Check for stale lock files
- Consider PostgreSQL for production with high concurrent writes

### Permission Denied
```
Error: Permission denied
```
**Solution**:
- Check file/directory permissions
- Run with appropriate user permissions
- Verify write access to `outputs/`, `logs/`, `database/` directories

## Dependencies

All dependencies are in `requirements.txt`:

```
fastapi              # Web framework
uvicorn[standard]    # ASGI server
pydantic            # Data validation
pydantic-settings   # Settings management
python-multipart    # File upload support
opencv-python       # Video/image processing
numpy               # Numerical operations
ultralytics         # YOLO model
torch               # PyTorch for ML
torchvision         # Vision utilities
```

Install all at once:
```bash
pip install -r requirements.txt
```

## Development Guide

### Adding New Endpoints

1. **Create route file** in `app/routes/`
   ```python
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/new", tags=["New"])
   
   @router.get("/endpoint")
   async def new_endpoint():
       return {"message": "New endpoint"}
   ```

2. **Define Pydantic models** in `app/db/models.py`
   ```python
   class NewRequest(BaseModel):
       field: str
   ```

3. **Implement service logic** in `app/services/`
   ```python
   class NewService:
       def process(self, data):
           # Business logic here
           pass
   ```

4. **Register router** in `app/main.py`
   ```python
   from app.routes import new_route
   app.include_router(new_route.router, prefix=settings.api_prefix)
   ```

### Code Guidelines

- ✅ Use type hints for all function signatures
- ✅ Add docstrings to all public functions
- ✅ Log all major operations (INFO level)
- ✅ Handle exceptions with meaningful messages
- ✅ Follow REST API conventions
- ✅ Keep routes thin (delegate to services)
- ✅ Separate concerns (routes, services, database)

### Project Architecture

```
Routes (HTTP Layer)
    ↓
Services (Business Logic)
    ↓
Model/Database (Data Layer)
    ↓
Utils (Helper Functions)
```

## Additional Resources

- **API Quick Guide**: See `API_GUIDE.md` for quick reference
- **Refactoring Summary**: See `REFACTORING_SUMMARY.md` for technical details
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **YOLO Docs**: https://docs.ultralytics.com/
- **OpenCV Docs**: https://docs.opencv.org/

## License

This project is for academic and educational purposes.

## Support

For issues, questions, or feature requests:
- Check the **API documentation**: http://localhost:8000/docs
- Review **API_GUIDE.md** for quick reference
- See **REFACTORING_SUMMARY.md** for technical details
- Check application logs in `logs/app.log`

---

**Project**: Smart Rickshaw Entry-Exit Monitoring System  
**Version**: 2.0.0  
**Last Updated**: December 2025  
**Python**: 3.10+  
**Framework**: FastAPI  
**Total Endpoints**: 13 API endpoints  
**Database**: SQLite with 4 tables  
**Features**: Detection, Tracking, Counting, Analytics, Export
