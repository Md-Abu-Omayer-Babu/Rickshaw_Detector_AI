# Smart Rickshaw Entry-Exit Monitoring System - Comprehensive Documentation

## 1. Project Overview

### Project Name
**Smart Rickshaw Entry-Exit Monitoring System**

### Purpose and Problem Statement
This system addresses the need for automated vehicle monitoring and counting at entry/exit points. Traditional manual counting methods are time-consuming, error-prone, and lack data analytics capabilities. This AI-powered solution provides real-time rickshaw detection, automated entry/exit counting, comprehensive analytics, and historical data management for traffic monitoring applications.

### High-Level Description
The system is a full-stack web application that uses deep learning-based computer vision (YOLOv8) to detect and track rickshaws in images, videos, and live CCTV/RTSP streams. It features:
- Real-time object detection and tracking
- Virtual line-based entry/exit counting
- Live video streaming with processing controls (pause/resume/stop)
- Comprehensive analytics dashboard with hourly and daily statistics
- Historical data management with filtering and export capabilities
- Multi-camera support for simultaneous stream processing

---

## 2. Key Features

### Detection Capabilities
- **Image Detection**: Upload single or multiple images for instant rickshaw detection with bounding boxes
- **Video Processing**: Frame-by-frame analysis with entry/exit line tracking and annotated video output
- **CCTV/RTSP Integration**: Real-time processing of live camera streams with continuous monitoring
- **Batch Processing**: Handle multiple files simultaneously for efficient processing
- **Live Preview**: Real-time preview during video processing with processing controls

### Entry-Exit Monitoring
- **Virtual Line Detection**: Configurable entry/exit lines using percentage-based positioning
- **Line Crossing Detection**: Accurate detection of rickshaws crossing virtual lines in either direction
- **Object Tracking**: IoU-based tracking to prevent duplicate counting of the same vehicle
- **Multi-Direction Support**: Differentiates between entry (bottom-to-top) and exit (top-to-bottom) movements
- **Historical Event Logging**: Detailed logs of every entry/exit event with timestamps, confidence scores, and bounding boxes

### Analytics & Reporting
- **Real-Time Dashboard**: Live statistics showing total counts, today's activity, and net counts
- **Hourly Distribution**: Hour-by-hour breakdown of traffic patterns for any given date
- **Daily Trends**: 7-day historical trend visualization
- **Peak Hour Analysis**: Automatic identification of busiest periods with detailed statistics
- **Camera-Based Filtering**: Filter analytics by specific cameras or view aggregate data

### Data Export
- **Multiple Formats**: Export data as CSV, JSON, or PDF
- **Flexible Filtering**: Filter exports by date range, event type, camera ID, and file type
- **Log Export**: Export detailed event logs with all metadata
- **Analytics Export**: Export summary analytics data

### Real-Time Processing Controls
- **Pause/Resume**: Pause and resume video processing at any point
- **Stop Processing**: Abort processing operations cleanly
- **Frame Navigation**: Skip forward/backward during processing
- **Live Status Updates**: Real-time progress updates with frame counts and processing status

### User Interface
- **Modern React Dashboard**: Responsive, intuitive UI built with React 19 and Tailwind CSS
- **Real-Time Updates**: Live detection statistics and processing status
- **Visual Feedback**: Loading states, progress indicators, and error handling
- **Date Range Pickers**: Easy filtering with date selection components
- **Export Buttons**: One-click export to multiple formats

---

## 3. Tech Stack

### Backend Technologies
- **Framework**: FastAPI 2.0.0 (High-performance async Python web framework)
- **Server**: Uvicorn (ASGI server with WebSocket support)
- **AI/ML Framework**: 
  - Ultralytics YOLOv8 (State-of-the-art object detection)
  - PyTorch (Deep learning backend)
- **Computer Vision**: OpenCV (cv2) for image/video processing
- **Database**: SQLite3 with optimized indexes
- **Validation**: Pydantic v2 (20+ data models with automatic validation)
- **PDF Generation**: xhtml2pdf for report generation
- **Python Version**: 3.12+

### Frontend Technologies
- **Framework**: React 19.2.0
- **Build Tool**: Vite 7.2.4 (Fast build and hot module replacement)
- **Styling**: Tailwind CSS 4.1.18 (Utility-first CSS framework)
- **Routing**: React Router DOM 7.11.0
- **HTTP Client**: Axios 1.13.2 (Promise-based HTTP client)
- **Icons**: Lucide React 0.562.0
- **Charts**: Recharts 3.6.0 (Composable charting library)
- **PDF Export**: jsPDF 3.0.4 with jspdf-autotable 5.0.2

### AI/ML Model
- **Architecture**: YOLOv8 (You Only Look Once - Version 8)
- **Training**: Custom-trained on rickshaw dataset
- **Model Format**: PyTorch (.pt file)
- **Inference Device**: Configurable (CPU/GPU)
- **Framework**: Ultralytics YOLO implementation

### Development Tools
- **Frontend Dev Server**: Vite with HMR (Hot Module Replacement)
- **Linting**: ESLint 9.39.1 with React plugins
- **Version Control**: Git
- **Package Managers**: pip (Python), npm (JavaScript)

---

## 4. Project Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React + Vite)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │Dashboard │  │ Image    │  │ Video    │  │  CCTV    │    │
│  │          │  │Detection │  │Detection │  │ Stream   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│  ┌──────────┐  ┌──────────┐                                │
│  │Analytics │  │ History  │                                │
│  └──────────┘  └──────────┘                                │
└─────────────────────────────────────────────────────────────┘
                            │
                    REST API (Axios)
                    HTTP + MJPEG Streaming
                            │
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + Uvicorn)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   API Routes Layer                    │   │
│  │  /detect  /cctv  /history  /logs  /analytics  /export│   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Service Layer                        │   │
│  │  InferenceService | VideoService | CCTVService       │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Core Business Logic                      │   │
│  │  YOLODetector | LineCrossingDetector | Tracker       │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Database Layer (SQLite)                  │   │
│  │  detections | rickshaw_logs | analytics_summary      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                    File System Storage
                            │
┌─────────────────────────────────────────────────────────────┐
│                    AI Model Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              YOLOv8 Detection Model                   │   │
│  │              (PyTorch Backend)                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Frontend-Backend Interaction

**Request Flow**:
1. User interacts with React UI (uploads file, requests data)
2. Axios API client makes HTTP request to FastAPI backend
3. FastAPI route handler validates request using Pydantic models
4. Service layer processes business logic
5. Database operations performed via SQLite connection
6. Response returned as JSON with Pydantic serialization
7. React UI updates with response data

**Streaming Flow** (CCTV/Video Preview):
1. User initiates stream processing
2. Backend starts processing in background thread
3. MJPEG stream endpoint serves frames via HTTP multipart
4. React UI displays live stream via `<img>` tag with stream URL
5. Status polling via separate REST endpoint for metadata

### Data Flow

**Image Detection**:
```
Upload Image → Validate → Save Temp → Detect (YOLO) → Draw Annotations 
→ Save Output → Insert DB Record → Return URL
```

**Video Detection with Counting**:
```
Upload Video → Validate → Open VideoCapture → For Each Frame:
  ├─ Detect Objects (YOLO)
  ├─ Update Tracker (IoU Matching)
  ├─ Check Line Crossing
  ├─ Log Events to DB
  └─ Draw Annotations
→ Write Output Video → Save Metadata → Return Stats
```

**CCTV Stream Processing**:
```
Connect RTSP → Start Background Thread → Continuous Loop:
  ├─ Read Frame
  ├─ Detect + Track + Count
  ├─ Log Events
  ├─ Update Job Manager Status
  └─ Encode Frame for Streaming
→ Serve via MJPEG Endpoint
```

### API Communication Pattern

- **RESTful API**: All data operations use REST principles
- **Multipart Form Data**: File uploads use `multipart/form-data`
- **JSON Responses**: All responses in JSON format with consistent structure
- **Error Handling**: Standardized error responses with HTTP status codes
- **CORS Enabled**: Cross-origin requests allowed for development
- **Static File Serving**: Processed images/videos served via `/outputs` endpoint
- **Stream Endpoints**: MJPEG streaming for live video preview

---

## 5. Folder Structure

### Backend Structure
```
backend/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   │
│   ├── core/                    # Core configuration and startup
│   │   ├── __init__.py
│   │   ├── config.py           # Settings class with 90+ configuration options
│   │   └── startup.py          # Application lifecycle (startup/shutdown events)
│   │
│   ├── db/                      # Database layer
│   │   ├── __init__.py
│   │   ├── database.py         # SQLite operations (15+ functions)
│   │   └── models.py           # Pydantic models for validation (20+ models)
│   │
│   ├── model/                   # AI model wrapper
│   │   ├── __init__.py
│   │   ├── best.pt             # YOLOv8 trained model weights
│   │   └── detector.py         # YOLODetector wrapper class
│   │
│   ├── routes/                  # API endpoint definitions
│   │   ├── __init__.py
│   │   ├── detect_image.py     # POST /api/detect/image
│   │   ├── detect_video.py     # POST /api/detect/video (sync & async)
│   │   ├── detect_cctv.py      # POST /api/cctv/start, /stop
│   │   ├── stream_video.py     # GET /api/stream/video/{job_id}
│   │   ├── stream_cctv.py      # GET /api/stream/cctv/{camera_id}
│   │   ├── history.py          # GET /api/history
│   │   ├── logs.py             # GET /api/logs
│   │   ├── analytics.py        # GET /api/analytics/*
│   │   └── export.py           # GET /api/export/logs, /analytics
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── inference_service.py    # Image detection service
│   │   ├── video_service.py        # Video processing with counting
│   │   ├── video_job_manager.py    # Video job state management
│   │   ├── cctv_service.py         # CCTV stream processing
│   │   └── cctv_job_manager.py     # CCTV stream state management
│   │
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── count_utils.py      # LineCrossingDetector, SimpleTracker (350+ lines)
│   │   ├── draw_utils.py       # Annotation drawing functions
│   │   └── file_utils.py       # File validation and handling
│   │
│   ├── outputs/                 # Generated output files
│   │   ├── images/             # Processed images
│   │   └── videos/             # Processed videos
│   │
│   └── templates/               # HTML templates (if needed)
│
├── database/                    # SQLite database storage
│   └── detections.db           # Main database file (4 tables)
│
├── logs/                        # Application logs
│   └── rickshaw_detection.log  # Rotating log file (10MB max, 5 backups)
│
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # Backend documentation
```

### Frontend Structure
```
frontend/
├── src/
│   ├── main.jsx                # React application entry point
│   ├── App.jsx                 # Root component with routing
│   ├── App.css                 # Global styles
│   ├── index.css              # Tailwind CSS imports
│   │
│   ├── api/                    # API communication layer
│   │   └── client.js          # Axios client with all API functions
│   │
│   ├── components/             # Reusable UI components
│   │   ├── ImageViewer.jsx    # Image display component
│   │   ├── Loader.jsx         # Loading spinner component
│   │   ├── StatCard.jsx       # Statistics card component
│   │   ├── UploadBox.jsx      # File upload component
│   │   └── VideoPlayer.jsx    # Video player component
│   │
│   ├── hooks/                  # Custom React hooks
│   │   └── useApi.js          # Custom hook for API calls
│   │
│   ├── layouts/                # Layout components
│   │   └── MainLayout.jsx     # Main layout with sidebar navigation
│   │
│   ├── pages/                  # Page components (routes)
│   │   ├── Dashboard.jsx      # Dashboard overview with statistics
│   │   ├── ImageDetection.jsx # Image upload and detection
│   │   ├── VideoDetection.jsx # Video upload with live preview
│   │   ├── CCTV.jsx           # CCTV stream management
│   │   ├── Analytics.jsx      # Detailed analytics page
│   │   └── History.jsx        # Detection history with filtering
│   │
│   └── utils/                  # Utility functions
│       └── formatters.js      # Number and date formatting
│
├── public/                     # Static assets
├── .env                        # Environment variables (VITE_API_URL)
├── index.html                  # HTML template
├── package.json                # NPM dependencies
├── vite.config.js             # Vite configuration
├── eslint.config.js           # ESLint configuration
└── README.md                   # Frontend documentation
```

### Key Directory Responsibilities

- **`backend/app/core`**: Application configuration, settings management, and lifecycle events
- **`backend/app/db`**: All database operations and Pydantic models for data validation
- **`backend/app/model`**: YOLOv8 model wrapper for object detection inference
- **`backend/app/routes`**: API endpoint definitions mapped to business logic
- **`backend/app/services`**: Business logic implementation (detection, counting, tracking)
- **`backend/app/utils`**: Helper functions for counting, drawing, and file operations
- **`frontend/src/api`**: Centralized API client for backend communication
- **`frontend/src/components`**: Reusable UI components
- **`frontend/src/pages`**: Full page components corresponding to routes

---

## 6. Core Components and Modules

### Backend Core Components

#### 1. YOLODetector (`app/model/detector.py`)
**Purpose**: Wrapper class for YOLOv8 model inference
**Key Methods**:
- `__init__(model_path, confidence, iou, device)`: Initialize model with configuration
- `detect(image)`: Run inference on image, returns DetectionResult
- `get_class_name(class_id)`: Get human-readable class name
- `count_rickshaws(detection_result)`: Count detected objects

**Interaction**: Used by all service classes for object detection

#### 2. InferenceService (`app/services/inference_service.py`)
**Purpose**: Handle image detection workflow
**Key Methods**:
- `process_image(file)`: Complete image processing pipeline
  - Saves uploaded file
  - Runs detection
  - Draws annotations
  - Saves output
  - Logs to database
  - Returns result with URL

**Interaction**: Called by `detect_image` route

#### 3. VideoService (`app/services/video_service.py`)
**Purpose**: Process video files with entry/exit counting
**Key Methods**:
- `process_video(file, enable_counting, camera_id)`: Synchronous video processing
- `process_video_with_live_preview(job_id, ...)`: Background processing with live preview

**Key Features**:
- Frame-by-frame detection and tracking
- Line crossing detection
- Real-time count updates
- Event logging to database
- Progress tracking via job manager

**Interaction**: Called by `detect_video` routes, uses LineCrossingDetector and SimpleTracker

#### 4. CCTVService (`app/services/cctv_service.py`)
**Purpose**: Process live RTSP/CCTV streams continuously
**Key Components**:
- `CCTVStreamProcessor`: Core stream processing class
  - Connection management with auto-reconnect
  - Frame processing loop
  - Entry/exit counting
  - MJPEG frame encoding for streaming
  
**Key Methods**:
- `start_continuous_stream(camera_id, rtsp_url)`: Start stream in background
- `stop_continuous_stream(camera_id)`: Stop active stream
- `get_stream_status(camera_id)`: Get current status and statistics

**Interaction**: Manages long-running background threads for continuous monitoring

#### 5. LineCrossingDetector (`app/utils/count_utils.py`)
**Purpose**: Detect when objects cross virtual lines for entry/exit counting
**Key Features**:
- Percentage-based line positioning
- Line intersection detection using computational geometry
- Object position history tracking
- Direction determination (entry vs exit)
- Duplicate crossing prevention

**Key Methods**:
- `update(object_id, bbox, frame_number)`: Update object position and check crossing
- `get_counts()`: Return entry, exit, and net counts
- `get_line_pixels()`: Convert percentage coordinates to pixels
- `reset_counts()`: Clear all counts and tracking data

**Algorithm**:
1. Track object center points across frames
2. Check if line segment (previous→current position) intersects counting line
3. Determine crossing direction based on which side of line
4. Increment appropriate counter and log event
5. Mark object as crossed to prevent duplicate counting

#### 6. SimpleTracker (`app/utils/count_utils.py`)
**Purpose**: Track objects across video frames using IoU matching
**Key Features**:
- Intersection over Union (IoU) based matching
- Unique ID assignment for each tracked object
- Track retention for temporary occlusions
- Automatic track cleanup for lost objects

**Key Methods**:
- `update(detections)`: Match new detections to existing tracks
- `_calculate_iou(box1, box2)`: Calculate overlap between bounding boxes

**Algorithm**:
1. For each new detection, find best matching existing track (highest IoU)
2. If IoU > threshold, update existing track
3. If no match, create new track with unique ID
4. Remove tracks that haven't been matched for max_frames_to_skip frames

#### 7. Database Module (`app/db/database.py`)
**Purpose**: SQLite database operations
**Key Functions**:
- `init_database()`: Create tables and indexes
- `insert_detection()`: Store detection record
- `get_all_detections()`: Retrieve detection history with filters
- `log_rickshaw_event()`: Log entry/exit events
- `get_rickshaw_logs()`: Retrieve event logs with filters
- `get_total_counts()`: Calculate aggregate statistics
- `get_daily_counts()`: Get counts for specific date
- `get_hourly_distribution()`: Hourly breakdown of events

**Context Manager**: `get_db_connection()` for automatic connection handling

### Frontend Core Components

#### 1. API Client (`src/api/client.js`)
**Purpose**: Centralized HTTP client for backend communication
**Key Functions**:
- `detectImage(file)`: Upload image for detection
- `detectVideoAsync(file, enableCounting, cameraId)`: Start async video processing
- `getJobStatus(jobId)`: Poll video processing status
- `startCCTVStream(request)`: Start CCTV stream
- `getCCTVStatus(cameraId)`: Get stream status
- `getDashboardAnalytics(cameraId)`: Fetch dashboard data
- `getHistory(filters)`: Get detection history
- `exportLogs(format, filters)`: Export data

**Configuration**:
- Base URL from environment variable
- 5-minute timeout for long operations
- Request/response interceptors for error handling

#### 2. Dashboard Component (`src/pages/Dashboard.jsx`)
**Purpose**: Main dashboard with real-time statistics
**Features**:
- All-time statistics (total entry, exit, net count)
- Today's activity summary
- Peak hour information
- Camera selection dropdown
- Auto-refresh on camera change

**Data Flow**: Fetches data from `/api/analytics/dashboard` on mount

#### 3. ImageDetection Component (`src/pages/ImageDetection.jsx`)
**Purpose**: Image upload and detection interface
**Features**:
- Drag-and-drop file upload
- File validation (image types only)
- Detection results display with annotated image
- Download button for processed image
- Error handling with user feedback

#### 4. VideoDetection Component (`src/pages/VideoDetection.jsx`)
**Purpose**: Video upload with live preview and processing controls
**Features**:
- Async video processing
- Live MJPEG preview during processing
- Pause/Resume/Stop controls
- Frame skip forward/backward
- Progress tracking with frame counts
- Final results display with statistics

**State Management**:
- Job ID for tracking processing
- Job status polling (2-second interval)
- Stream retry mechanism
- Pause state synchronization

#### 5. CCTV Component (`src/pages/CCTV.jsx`)
**Purpose**: CCTV stream management interface
**Features**:
- RTSP URL input and connection testing
- Start/Stop stream controls
- Live MJPEG stream preview
- Real-time statistics (entry, exit, FPS)
- Multi-camera support

#### 6. History Component (`src/pages/History.jsx`)
**Purpose**: Detection history with filtering
**Features**:
- Date range filtering
- File type filtering
- Tabular data display
- Export to CSV/JSON
- Pagination (if implemented)

---

## 7. API Documentation

### Detection Endpoints

#### POST `/api/detect/image`
**Purpose**: Detect rickshaws in uploaded image
**Request**: `multipart/form-data`
- `file`: Image file (JPG, PNG, BMP, WEBP)

**Response**: `200 OK`
```json
{
  "success": true,
  "file_name": "uuid-generated-name.jpg",
  "rickshaw_count": 5,
  "output_url": "/outputs/images/uuid-generated-name.jpg",
  "message": "Image processed successfully"
}
```

**Errors**: 
- `400`: Invalid file format or type
- `500`: Processing error

---

#### POST `/api/detect/video`
**Purpose**: Synchronous video processing with entry/exit counting
**Request**: `multipart/form-data` with query parameters
- `file`: Video file (MP4, AVI, MOV, MKV)
- `enable_counting` (query): Boolean, default `true`
- `camera_id` (query): String, default `"default"`

**Response**: `200 OK`
```json
{
  "success": true,
  "file_name": "uuid-generated-name.mp4",
  "rickshaw_count": 12,
  "total_entry": 45,
  "total_exit": 38,
  "net_count": 7,
  "output_url": "/outputs/videos/uuid-generated-name.mp4",
  "message": "Video processed successfully"
}
```

---

#### POST `/api/detect/video/async`
**Purpose**: Start background video processing with live preview support
**Request**: Same as `/detect/video`

**Response**: `200 OK`
```json
{
  "success": true,
  "job_id": "uuid-job-id",
  "message": "Video processing started. Use /api/stream/video/{job_id} for live preview."
}
```

**Usage Flow**:
1. Call this endpoint to start processing
2. Use returned `job_id` to stream preview: `GET /api/stream/video/{job_id}`
3. Poll status: `GET /api/detect/video/status/{job_id}`

---

#### GET `/api/detect/video/status/{job_id}`
**Purpose**: Get status of async video processing job
**Response**: `200 OK`
```json
{
  "job_id": "uuid-job-id",
  "status": "processing",
  "progress": 45.5,
  "processed_frames": 455,
  "total_frames": 1000,
  "entry_count": 12,
  "exit_count": 8,
  "net_count": 4,
  "result": null
}
```

**Status Values**: `"processing"`, `"completed"`, `"failed"`, `"stopped"`, `"paused"`

---

### CCTV Stream Endpoints

#### POST `/api/cctv/start`
**Purpose**: Start continuous CCTV stream processing
**Request**: `application/json`
```json
{
  "camera_id": "camera-001",
  "rtsp_url": "rtsp://username:password@ip:port/stream",
  "camera_name": "Front Gate Camera"
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "camera_id": "camera-001",
  "message": "Stream started successfully",
  "stream_url": "/api/stream/cctv/camera-001"
}
```

---

#### POST `/api/cctv/stop/{camera_id}`
**Purpose**: Stop running CCTV stream
**Response**: `200 OK`
```json
{
  "success": true,
  "camera_id": "camera-001",
  "message": "Stream stopped successfully",
  "final_stats": {
    "entry_count": 245,
    "exit_count": 238,
    "frames_processed": 45678
  }
}
```

---

#### GET `/api/cctv/status/{camera_id}`
**Purpose**: Get current status of CCTV stream
**Response**: `200 OK`
```json
{
  "success": true,
  "camera_id": "camera-001",
  "camera_name": "Front Gate Camera",
  "status": "running",
  "entry_count": 245,
  "exit_count": 238,
  "net_count": 7,
  "frames_processed": 45678,
  "fps": 14.5,
  "uptime": 3145.2,
  "stream_properties": {
    "width": 1920,
    "height": 1080,
    "fps": 15
  }
}
```

---

#### POST `/api/cctv/stream/test`
**Purpose**: Test RTSP connection without full processing
**Request**: Same as `/cctv/start`
**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Connection successful",
  "stream_properties": {
    "width": 1920,
    "height": 1080,
    "fps": 15
  }
}
```

---

### Streaming Endpoints

#### GET `/api/stream/video/{job_id}`
**Purpose**: MJPEG stream of video being processed
**Response**: `multipart/x-mixed-replace` (MJPEG stream)
- Continuous stream of JPEG frames
- Use in `<img src="/api/stream/video/{job_id}">` for live preview

---

#### GET `/api/stream/cctv/{camera_id}`
**Purpose**: MJPEG stream of live CCTV feed
**Response**: `multipart/x-mixed-replace` (MJPEG stream)
- Continuous stream of annotated frames
- Use in `<img src="/api/stream/cctv/{camera_id}">`

---

### Analytics Endpoints

#### GET `/api/analytics/dashboard`
**Purpose**: Get comprehensive dashboard analytics
**Query Parameters**:
- `camera_id`: String, default `"default"`

**Response**: `200 OK`
```json
{
  "success": true,
  "total_entry": 1245,
  "total_exit": 1180,
  "net_count": 65,
  "today_entry": 45,
  "today_exit": 38,
  "today_net": 7,
  "hourly_distribution": [
    {"hour": "00", "event_type": "entry", "count": 2},
    {"hour": "00", "event_type": "exit", "count": 1}
  ],
  "peak_hour": {
    "hour": 14,
    "entry_count": 12,
    "exit_count": 10,
    "total_count": 22
  },
  "daily_trend": [
    {
      "date": "2026-01-20",
      "entry_count": 52,
      "exit_count": 48,
      "net_count": 4
    }
  ]
}
```

---

#### GET `/api/analytics/daily`
**Purpose**: Get daily counts for specific date
**Query Parameters**:
- `date`: String (YYYY-MM-DD), required
- `camera_id`: String, default `"default"`

**Response**: `200 OK`
```json
{
  "date": "2026-01-26",
  "entry_count": 45,
  "exit_count": 38,
  "net_count": 7
}
```

---

#### GET `/api/analytics/hourly`
**Purpose**: Get hourly distribution for specific date
**Query Parameters**:
- `date`: String (YYYY-MM-DD), required
- `camera_id`: String, default `"default"`

**Response**: `200 OK` - Array of hourly counts
```json
[
  {"hour": "00", "event_type": "entry", "count": 2},
  {"hour": "00", "event_type": "exit", "count": 1},
  {"hour": "01", "event_type": "entry", "count": 3}
]
```

---

### History and Logs Endpoints

#### GET `/api/history`
**Purpose**: Get detection history records
**Query Parameters**:
- `start_date`: String (YYYY-MM-DD), optional
- `end_date`: String (YYYY-MM-DD), optional
- `file_type`: String (`"image"` or `"video"`), optional

**Response**: `200 OK`
```json
{
  "success": true,
  "total_records": 150,
  "detections": [
    {
      "id": 1,
      "file_type": "video",
      "file_name": "uuid-name.mp4",
      "rickshaw_count": 12,
      "created_at": "2026-01-26T10:30:00"
    }
  ]
}
```

---

#### GET `/api/logs`
**Purpose**: Get rickshaw event logs
**Query Parameters**:
- `start_date`: DateTime (ISO format), optional
- `end_date`: DateTime (ISO format), optional
- `event_type`: String (`"entry"` or `"exit"`), optional
- `camera_id`: String, optional
- `limit`: Integer (1-10000), default 1000

**Response**: `200 OK`
```json
{
  "success": true,
  "total_records": 500,
  "logs": [
    {
      "id": 1,
      "event_type": "entry",
      "camera_id": "default",
      "rickshaw_id": "track_123",
      "confidence": 0.89,
      "timestamp": "2026-01-26T10:30:15",
      "frame_number": 450,
      "bounding_box": "[100, 200, 300, 400]",
      "crossing_line": "entry_line",
      "notes": null
    }
  ]
}
```

---

### Export Endpoints

#### GET `/api/export/logs`
**Purpose**: Export event logs as CSV or JSON
**Query Parameters**:
- `format`: String (`"csv"` or `"json"`), required
- `start_date`: String (YYYY-MM-DD), optional
- `end_date`: String (YYYY-MM-DD), optional
- `event_type`: String (`"entry"` or `"exit"`), optional
- `camera_id`: String, optional
- `limit`: Integer (1-100000), default 10000

**Response**: 
- `200 OK`: File download (`text/csv` or `application/json`)
- `404`: No logs found matching criteria
- `400`: Invalid parameters

**Download Filename**: `rickshaw_logs_YYYYMMDD_HHMMSS.{format}`

---

### Utility Endpoints

#### GET `/`
**Purpose**: API root with endpoint documentation
**Response**: JSON with all available endpoints

#### GET `/health`
**Purpose**: Health check endpoint
**Response**: `200 OK`
```json
{
  "status": "healthy",
  "service": "Smart Rickshaw Entry-Exit Monitoring System",
  "version": "2.0.0"
}
```

---

## 8. Database Design

### Database Type
**SQLite3** - Lightweight, serverless, file-based relational database

### Database Location
`backend/database/detections.db`

### Tables

#### 1. `detections`
**Purpose**: Store basic detection records for processed files

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increment unique identifier |
| `file_type` | TEXT NOT NULL | File type: "image" or "video" |
| `file_name` | TEXT NOT NULL | Generated unique filename |
| `rickshaw_count` | INTEGER NOT NULL | Number of rickshaws detected |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Detection timestamp |

**Usage**: Stores one record per processed image/video for history tracking

---

#### 2. `rickshaw_logs`
**Purpose**: Detailed event log for each entry/exit occurrence

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increment unique identifier |
| `event_type` | TEXT NOT NULL | Event type: "entry" or "exit" |
| `camera_id` | TEXT DEFAULT 'default' | Camera identifier |
| `rickshaw_id` | TEXT | Tracking ID from SimpleTracker |
| `confidence` | REAL NOT NULL | Detection confidence (0.0-1.0) |
| `timestamp` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Event timestamp |
| `frame_number` | INTEGER | Frame number in video/stream |
| `bounding_box` | TEXT | JSON string: `[x1, y1, x2, y2]` |
| `crossing_line` | TEXT | Line identifier that was crossed |
| `notes` | TEXT | Additional metadata |

**Indexes**:
- `idx_rickshaw_logs_timestamp` on `timestamp`
- `idx_rickshaw_logs_event_type` on `event_type`
- `idx_rickshaw_logs_camera` on `camera_id`

**Usage**: One record per line crossing event for detailed analytics

---

#### 3. `analytics_summary`
**Purpose**: Cached daily summary statistics for performance

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increment unique identifier |
| `date` | DATE NOT NULL | Summary date (YYYY-MM-DD) |
| `camera_id` | TEXT DEFAULT 'default' | Camera identifier |
| `total_entry` | INTEGER DEFAULT 0 | Total entries for the day |
| `total_exit` | INTEGER DEFAULT 0 | Total exits for the day |
| `net_count` | INTEGER DEFAULT 0 | Net count (entry - exit) |
| `peak_hour` | INTEGER | Hour with most activity (0-23) |
| `peak_hour_count` | INTEGER | Count during peak hour |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Unique Constraint**: `(date, camera_id)`

**Index**: `idx_analytics_date` on `date`

**Usage**: Pre-computed daily summaries for fast dashboard loading

---

#### 4. `camera_streams`
**Purpose**: Track registered camera streams and their status

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increment unique identifier |
| `camera_id` | TEXT UNIQUE NOT NULL | Unique camera identifier |
| `camera_name` | TEXT NOT NULL | Human-readable camera name |
| `rtsp_url` | TEXT NOT NULL | RTSP stream URL |
| `status` | TEXT DEFAULT 'inactive' | Current status: "active", "inactive", "error" |
| `last_active` | TIMESTAMP | Last activity timestamp |
| `total_frames_processed` | INTEGER DEFAULT 0 | Lifetime frame count |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Registration timestamp |

**Usage**: Camera registry and status tracking

---

### Key Relationships

- **detections** → Standalone records (no foreign keys)
- **rickshaw_logs** → Linked by `camera_id` to camera_streams (logical, not enforced FK)
- **analytics_summary** → Aggregated from rickshaw_logs
- **camera_streams** → Referenced by logs via `camera_id`

### Data Flow

1. **Image/Video Detection**: Insert record into `detections` table
2. **Entry/Exit Event**: Insert record into `rickshaw_logs` table
3. **Daily Summary**: Update or insert into `analytics_summary` (can be triggered or computed on-demand)
4. **Camera Registration**: Insert/update `camera_streams` when stream starts

### Query Optimization

- **Indexes**: Created on frequently queried columns (timestamp, event_type, camera_id, date)
- **Row Factory**: `sqlite3.Row` enables column access by name
- **Connection Pooling**: Context manager ensures proper connection handling
- **Transaction Management**: Automatic commit/rollback in context manager

---

## 9. Configuration and Environment Variables

### Backend Configuration

#### Configuration File: `backend/app/core/config.py`
Uses **Pydantic Settings** for type-safe configuration management.

#### Key Configuration Categories

**Application Info**:
```python
app_name: str = "Smart Rickshaw Entry-Exit Monitoring System"
version: str = "2.0.0"
description: str = "FastAPI backend for rickshaw detection..."
api_prefix: str = "/api"
debug: bool = True
```

**CORS Settings**:
```python
cors_origins: List[str] = ["*"]  # Allow all origins in dev
cors_allow_credentials: bool = True
cors_allow_methods: List[str] = ["*"]
cors_allow_headers: List[str] = ["*"]
```

**File Upload Settings**:
```python
max_upload_size: int = 500 * 1024 * 1024  # 500 MB
allowed_image_extensions: set = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
allowed_video_extensions: set = {".mp4", ".avi", ".mov", ".mkv"}
```

**Path Settings**:
```python
base_dir: Path = Path(__file__).resolve().parent.parent.parent
model_path: Path = base_dir / "app" / "model" / "best.pt"
outputs_dir: Path = base_dir / "outputs"
images_output_dir: Path = outputs_dir / "images"
videos_output_dir: Path = outputs_dir / "videos"
database_path: Path = base_dir / "database" / "detections.db"
logs_dir: Path = base_dir / "logs"
```

**YOLO Model Settings**:
```python
yolo_confidence: float = 0.25  # Detection confidence threshold
yolo_iou: float = 0.45  # IoU threshold for NMS
yolo_device: str = "cpu"  # Device for inference ("cpu" or "cuda")
target_class: str = "rickshaw"
```

**Entry-Exit Line Settings** (Percentage-based):
```python
entry_line_start: Tuple[float, float] = (0.0, 50.0)  # Left edge, 50% height
entry_line_end: Tuple[float, float] = (100.0, 50.0)  # Right edge, 50% height
```

**Counting Algorithm Settings**:
```python
crossing_threshold: int = 5  # Pixels for side determination
min_detection_confidence: float = 0.3
track_history_length: int = 30  # Number of positions to keep
```

**Video Processing Optimization**:
```python
enable_live_preview: bool = False
preview_update_interval: int = 5  # Update every N frames
frame_skip: int = 30  # Process every Nth frame (optimization)
detection_scale_factor: float = 0.75  # Scale factor for detection
use_fast_codec: bool = False
```

**CCTV/RTSP Settings**:
```python
max_concurrent_streams: int = 4
stream_reconnect_attempts: int = 3
stream_reconnect_delay: int = 5  # Seconds between retries
stream_fps_limit: int = 15  # Max FPS for CCTV processing
```

**Logging Settings**:
```python
log_level: str = "INFO"
log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_file: str = "rickshaw_detection.log"
log_max_bytes: int = 10 * 1024 * 1024  # 10 MB
log_backup_count: int = 5  # Number of backup log files
```

#### Environment File Support

Create `.env` file in `backend/` directory:
```env
DEBUG=True
YOLO_DEVICE=cuda
YOLO_CONFIDENCE=0.30
MAX_CONCURRENT_STREAMS=8
LOG_LEVEL=DEBUG
```

Settings automatically load from `.env` via Pydantic's `env_file` config.

---

### Frontend Configuration

#### Environment Variables File: `frontend/.env`

```env
# Backend API URL
VITE_API_URL=http://localhost:8000
```

**Usage in Code**:
```javascript
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

**Note**: Vite requires `VITE_` prefix for environment variables to be exposed to client-side code.

#### Configuration in `vite.config.js`

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

---

## 10. Setup and Run Instructions

### Prerequisites

#### Backend Requirements
- **Python**: 3.12 or higher
- **pip**: Python package manager
- **CUDA Toolkit** (Optional): For GPU acceleration
- **Git**: For cloning repository

#### Frontend Requirements
- **Node.js**: 16.x or higher
- **npm**: 7.x or higher (comes with Node.js)

#### System Requirements
- **RAM**: Minimum 4GB (8GB recommended for video processing)
- **Storage**: 2GB free space for dependencies and outputs
- **OS**: Windows, Linux, or macOS

---

### Installation Steps

#### 1. Clone Repository
```bash
git clone <repository-url>
cd Rickshaw_Detector
```

#### 2. Backend Setup

**Navigate to backend directory**:
```bash
cd backend
```

**Create virtual environment**:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**Install dependencies**:
```bash
pip install -r requirements.txt
```

**Verify model file exists**:
```bash
# Check if best.pt exists
dir app\model\best.pt  # Windows
ls app/model/best.pt   # Linux/Mac
```

If model file is missing, place your trained YOLOv8 model (`best.pt`) in `backend/app/model/`.

**Create necessary directories** (auto-created on startup, but can create manually):
```bash
mkdir -p outputs/images outputs/videos database logs
```

#### 3. Frontend Setup

**Navigate to frontend directory** (from project root):
```bash
cd frontend
```

**Install dependencies**:
```bash
npm install
```

**Configure environment**:
```bash
# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
```

---

### Running the Project

#### Start Backend Server

**From backend directory**:
```bash
# Activate virtual environment first (if not already activated)
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Run the server
python run.py
```

**Expected Output**:
```
Smart Rickshaw Entry-Exit Monitoring System
                Version 2.0.0

Starting server...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Server Details**:
- URL: `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/docs`
- Alternative Docs (ReDoc): `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

#### Start Frontend Development Server

**From frontend directory**:
```bash
npm run dev
```

**Expected Output**:
```
VITE v7.2.4  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: http://192.168.1.x:3000/
```

**Access Application**: Open browser to `http://localhost:3000`

---

### Common Commands

#### Backend Commands

**Run in debug mode** (default):
```bash
python run.py
```

**Run in production mode**:
```bash
# Modify settings.debug in config.py or set environment variable
export DEBUG=False  # Linux/Mac
set DEBUG=False     # Windows
python run.py
```

**Run with Uvicorn directly** (for advanced users):
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Commands

**Development server** (with hot reload):
```bash
npm run dev
```

**Production build**:
```bash
npm run build
```

**Preview production build**:
```bash
npm run preview
```

**Linting**:
```bash
npm run lint
```

---

### Production Deployment

#### Backend Production Setup

**Install production ASGI server**:
```bash
pip install gunicorn uvicorn[standard]
```

**Run with Gunicorn** (Linux/Mac):
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

**Run with systemd service** (Linux):
Create `/etc/systemd/system/rickshaw-api.service`:
```ini
[Unit]
Description=Rickshaw Detection API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

**Start service**:
```bash
sudo systemctl start rickshaw-api
sudo systemctl enable rickshaw-api
```

#### Frontend Production Setup

**Build for production**:
```bash
npm run build
# Output in dist/ directory
```

**Serve with nginx**:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### Troubleshooting

**Backend won't start**:
- Check Python version: `python --version` (should be 3.12+)
- Verify model file exists: `ls app/model/best.pt`
- Check port 8000 is not in use: `netstat -an | grep 8000`

**Frontend can't connect to backend**:
- Verify backend is running: `curl http://localhost:8000/health`
- Check `.env` file has correct `VITE_API_URL`
- Check browser console for CORS errors

**Video processing fails**:
- Check available RAM (videos require significant memory)
- Reduce `detection_scale_factor` in config
- Increase `frame_skip` to process fewer frames

**CCTV stream won't connect**:
- Test RTSP URL with VLC media player first
- Check network connectivity to camera
- Verify credentials in RTSP URL
- Try increasing `stream_reconnect_delay`

---

## 11. Error Handling and Logging

### Backend Error Handling

#### Global Exception Handler
Located in `app/main.py`, catches all unhandled exceptions:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )
```

**Behavior**:
- In debug mode: Returns full error details
- In production: Returns generic error message
- Always logs full stack trace

#### HTTP Exception Handling
FastAPI's built-in `HTTPException` for API errors:
```python
raise HTTPException(
    status_code=400,
    detail="Invalid file format. Allowed formats: .jpg, .png"
)
```

**Common Status Codes**:
- `400`: Bad request (validation errors, invalid input)
- `404`: Resource not found (job ID, camera ID)
- `500`: Internal server error (processing failures)

#### Validation Error Handling
Pydantic automatically validates request bodies and query parameters:
```python
class CCTVStartRequest(BaseModel):
    camera_id: str
    rtsp_url: str
    camera_name: Optional[str] = "Camera"
```

Invalid requests return `422 Unprocessable Entity` with detailed error messages.

#### Database Error Handling
Context manager in `database.py` handles database errors:
```python
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(settings.database_path)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise e
    finally:
        conn.close()
```

**Features**:
- Automatic commit on success
- Automatic rollback on error
- Always closes connection
- Logs all database errors

#### File Processing Error Handling
Services include cleanup on errors:
```python
try:
    # Process file
    result = await process_image(file)
except Exception as e:
    # Clean up temporary files
    if temp_path.exists():
        temp_path.unlink()
    raise e
```

### Frontend Error Handling

#### Axios Interceptors
Centralized error handling in `src/api/client.js`:
```javascript
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      if (status === 400) {
        console.error('Bad Request:', data.detail);
      } else if (status === 404) {
        console.error('Not Found:', data.detail);
      } else if (status === 500) {
        console.error('Server Error:', data.detail);
      }
    } else if (error.request) {
      console.error('Network Error: No response from server');
    }
    return Promise.reject(error);
  }
);
```

#### Component-Level Error Handling
Each page component handles errors with user-friendly messages:
```javascript
const [error, setError] = useState(null);

try {
  const result = await detectImage(file);
  setResult(result);
} catch (err) {
  setError(err.response?.data?.detail || 'Failed to process image');
}

// Display error
{error && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-6">
    <p className="text-red-800">{error}</p>
  </div>
)}
```

---

### Logging Strategy

#### Backend Logging Configuration

**Logger Setup** (`app/core/config.py`):
```python
def setup_logging():
    logger = logging.getLogger("rickshaw_detection")
    logger.setLevel(logging.INFO)
    
    # Rotating file handler (10 MB max, 5 backups)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Both handlers use the same format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

**Log Levels Used**:
- `DEBUG`: Detailed diagnostic information (frame processing, tracking updates)
- `INFO`: General informational messages (startup, request handling, counts)
- `WARNING`: Warning messages (reconnection attempts, skipped frames)
- `ERROR`: Error conditions (processing failures, database errors)

**Log File Management**:
- Location: `backend/logs/rickshaw_detection.log`
- Max Size: 10 MB per file
- Rotation: 5 backup files kept
- Naming: `rickshaw_detection.log`, `rickshaw_detection.log.1`, etc.

#### Key Logging Points

**Application Lifecycle**:
```python
logger.info("Starting Rickshaw Detection API Server")
logger.info("YOLO model loaded successfully")
logger.info("Application startup complete")
```

**Request Processing**:
```python
logger.info(f"Video detection request: {file.filename}")
logger.info(f"Video processing complete: {frame_count} frames")
```

**Entry/Exit Events**:
```python
logger.info(f"Entry detected: object {track_id} at frame {frame_number}")
logger.info(f"Exit detected: object {track_id} at frame {frame_number}")
```

**Error Conditions**:
```python
logger.error(f"Error processing video: {str(e)}", exc_info=True)
logger.error(f"Failed to connect to stream: {rtsp_url}")
```

**Database Operations**:
```python
logger.info(f"Inserted detection record: {file_type} - {file_name}")
logger.error(f"Database error: {str(e)}")
```

#### Frontend Logging

**Console Logging**:
- Development: Full error stack traces
- Production: Limited error information

**Usage**:
```javascript
console.log('Fetching dashboard data for camera:', cameraId);
console.error('Error processing image:', err);
console.warn('Stream retry attempt:', retryCount);
```

---

## 12. Performance and Optimization

### Video Processing Optimizations

#### Frame Skipping
**Configuration**: `frame_skip` setting in `config.py`
```python
frame_skip: int = 30  # Process every 30th frame
```
**Impact**: Reduces processing time by 97% (30fps → 1fps effective)
**Trade-off**: May miss fast-moving objects

#### Detection Scaling
**Configuration**: `detection_scale_factor` setting
```python
detection_scale_factor: float = 0.75  # Scale to 75% of original
```
**Impact**: 
- 75% scale = 56% fewer pixels to process
- Faster inference with minimal accuracy loss

#### Codec Selection
**Configuration**: `use_fast_codec` setting
```python
use_fast_codec: bool = False  # Set True for faster encoding
```
**Options**:
- `False`: Uses MP4V (better quality, slower)
- `True`: Uses XVID (faster, lower quality)

---

### CCTV Stream Optimizations

#### FPS Limiting
**Configuration**: `stream_fps_limit` setting
```python
stream_fps_limit: int = 15  # Max 15 FPS
```
**Impact**: Reduces CPU usage for high FPS cameras

#### Concurrent Stream Management
**Configuration**: `max_concurrent_streams` setting
```python
max_concurrent_streams: int = 4  # Max 4 simultaneous streams
```
**Impact**: Prevents resource exhaustion from too many streams

#### Connection Management
- **Auto-reconnect**: Up to 3 attempts with 5-second delays
- **Error recovery**: Graceful handling of connection drops
- **Resource cleanup**: Proper VideoCapture release

---

### Database Optimizations

#### Indexes
```sql
CREATE INDEX idx_rickshaw_logs_timestamp ON rickshaw_logs(timestamp);
CREATE INDEX idx_rickshaw_logs_event_type ON rickshaw_logs(event_type);
CREATE INDEX idx_rickshaw_logs_camera ON rickshaw_logs(camera_id);
CREATE INDEX idx_analytics_date ON analytics_summary(date);
```
**Impact**: Fast queries on filtered data (date ranges, event types)

#### Connection Pooling
Context manager ensures efficient connection handling:
- Single connection per query
- Automatic commit/rollback
- Always closes connections

#### Row Factory
```python
conn.row_factory = sqlite3.Row
```
**Impact**: Enables column access by name without overhead

---

### Background Processing

#### Async Video Processing
**Implementation**: `detect_video_async` endpoint
- Returns job ID immediately
- Processing happens in background thread
- Non-blocking for other requests

**Benefits**:
- User doesn't wait for long video processing
- Can process multiple videos simultaneously
- Live preview available during processing

#### Thread Management
```python
processing_thread = threading.Thread(
    target=video_service.process_video_with_live_preview,
    args=(job_id, temp_input_path, output_filename),
    daemon=True
)
processing_thread.start()
```
**Features**:
- Daemon threads auto-cleanup on shutdown
- Separate thread per video job
- Thread-safe job status updates

---

### Memory Management

#### Chunked File Uploads
```python
chunk_size = 1024 * 1024  # 1 MB chunks
with open(destination_path, "wb") as f:
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        f.write(chunk)
```
**Impact**: Can handle large files without loading entire file into memory

#### Frame Processing
- Frames processed one at a time
- No accumulation of processed frames in memory
- VideoWriter streams output directly to disk

#### Track History Limits
```python
track_history_length: int = 30  # Keep only last 30 positions
```
**Impact**: Prevents unlimited memory growth from tracking data

---

### Frontend Optimizations

#### Lazy Loading
- Components loaded on-demand via React Router
- Images loaded only when needed

#### Debouncing
- Status polling at reasonable intervals (2 seconds)
- Prevents excessive API calls

#### Efficient Re-renders
- `useState` and `useEffect` properly managed
- Conditional rendering to avoid unnecessary updates

---

### Caching Strategy

#### Analytics Summary Table
Pre-computed daily summaries avoid expensive aggregations:
```sql
-- Instead of aggregating logs every dashboard load
SELECT SUM(...) FROM rickshaw_logs WHERE date = today

-- Use cached summary
SELECT * FROM analytics_summary WHERE date = today
```

---

## 13. Security Considerations

### Input Validation

#### File Type Validation
**Backend validation** (`app/utils/file_utils.py`):
```python
# Extension check
if extension not in settings.allowed_image_extensions:
    raise HTTPException(status_code=400, detail="Invalid format")

# Content-type check
if not file.content_type.startswith("image/"):
    raise HTTPException(status_code=400, detail="Invalid file type")
```

**Impact**: Prevents upload of malicious files

#### Request Validation
**Pydantic models** enforce schema validation:
```python
class CCTVStartRequest(BaseModel):
    camera_id: str
    rtsp_url: str
    camera_name: Optional[str] = "Camera"
```
**Impact**: Automatic validation of all request data

---

### Authentication and Authorization

**Current Implementation**: None (suitable for internal/trusted networks)

**Recommendations for Production**:
1. **API Key Authentication**: Add API key header validation
2. **JWT Tokens**: Implement user authentication with JWT
3. **Role-Based Access**: Differentiate admin vs. viewer permissions
4. **OAuth 2.0**: For enterprise integration

**Example Implementation** (not included):
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials):
    # Validate token
    pass

@router.post("/detect/image", dependencies=[Depends(get_current_user)])
async def detect_image(file: UploadFile):
    pass
```

---

### Data Protection

#### File Storage Security
- **Unique Filenames**: UUID-based naming prevents overwrites and guessing
- **Isolated Directories**: Separate folders for images/videos
- **No Direct Access**: Files served through FastAPI, not web server root

#### Database Security
- **SQLite File Permissions**: Should be restricted to application user
- **SQL Injection Prevention**: Parameterized queries used throughout
  ```python
  cursor.execute("SELECT * FROM logs WHERE camera_id = ?", (camera_id,))
  ```

#### Sensitive Data Handling
- **RTSP URLs**: Contain credentials, logged carefully
- **No Password Logging**: Passwords not logged in plain text
- **Environment Variables**: Credentials should be in `.env`, not code

---

### CORS Configuration

**Current Settings** (Development):
```python
cors_origins: List[str] = ["*"]  # Allow all origins
cors_allow_credentials: bool = True
cors_allow_methods: List[str] = ["*"]
cors_allow_headers: List[str] = ["*"]
```

**Production Recommendations**:
```python
cors_origins: List[str] = [
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]
cors_allow_credentials: bool = True
cors_allow_methods: List[str] = ["GET", "POST"]
cors_allow_headers: List[str] = ["Content-Type", "Authorization"]
```

---

### Network Security

#### HTTPS in Production
- Deploy behind reverse proxy (nginx/Apache)
- Use SSL/TLS certificates (Let's Encrypt)
- Enforce HTTPS redirects

#### RTSP Stream Security
- Use strong passwords in RTSP URLs
- Restrict network access to camera subnets
- Consider VPN for remote camera access

---

### Resource Limits

#### File Size Limits
```python
max_upload_size: int = 500 * 1024 * 1024  # 500 MB
```

#### Concurrent Processing Limits
```python
max_concurrent_streams: int = 4  # Prevent resource exhaustion
```

#### Query Limits
```python
limit: int = Query(10000, ge=1, le=100000)  # Max records per export
```

**Impact**: Prevents denial-of-service from large requests

---

### Error Information Disclosure

**Debug Mode** (Development):
```python
"detail": str(exc)  # Full error details
```

**Production Mode**:
```python
"detail": "An unexpected error occurred" if not settings.debug else str(exc)
```

**Impact**: Prevents leaking internal system details in production

---

### Recommendations for Enhanced Security

1. **Implement Authentication**: Add JWT-based authentication
2. **API Rate Limiting**: Prevent abuse (use libraries like `slowapi`)
3. **Input Sanitization**: Additional validation for RTSP URLs, file paths
4. **Audit Logging**: Log all API access and administrative actions
5. **Secrets Management**: Use proper secrets management (Azure Key Vault, AWS Secrets Manager)
6. **Container Security**: Run in containers with minimal privileges
7. **Regular Updates**: Keep dependencies updated (`pip-audit`, `npm audit`)

---

## 14. Limitations and Known Issues

### Current Limitations

#### 1. Model Performance
- **Single Class Detection**: Model trained only for rickshaws, cannot detect other vehicles
- **Lighting Sensitivity**: Performance degrades in low-light or nighttime conditions
- **Occlusion Handling**: Partially occluded vehicles may not be detected
- **Small Object Detection**: Distant rickshaws may be missed
- **Model Accuracy**: Depends on training data quality and diversity

#### 2. Tracking Limitations
- **ID Switching**: Objects may lose tracking IDs during heavy occlusion
- **Fast Movement**: Very fast-moving objects may not be tracked correctly
- **Crowded Scenes**: Tracking accuracy decreases with many overlapping objects
- **No Re-identification**: Lost tracks are not recovered if object reappears

#### 3. Entry-Exit Counting
- **Single Line Only**: System uses one horizontal counting line
- **Bidirectional Ambiguity**: Difficult to differentiate complex movement patterns
- **Frame Rate Dependency**: Low frame rates may miss fast crossings
- **No Cross-Frame Validation**: Counts cannot be corrected after the fact

#### 4. Video Processing
- **Processing Time**: Large videos take significant time (not real-time)
- **Memory Usage**: High-resolution videos require substantial RAM
- **No Pause on Sync**: Synchronous endpoint cannot pause/resume
- **Codec Limitations**: Output always in MP4V format (compatibility issues on some players)

#### 5. CCTV Stream Processing
- **Network Dependency**: Stream interruptions cause data loss
- **No Buffering**: Cannot reprocess past frames
- **Limited Reconnect**: Only 3 reconnect attempts before giving up
- **No Recording**: Continuous streams not saved to disk

#### 6. Database Performance
- **SQLite Limitations**: Not suitable for very high-volume concurrent writes
- **No Distributed Support**: Cannot scale across multiple servers
- **File Locking**: Single-writer limitation may cause bottlenecks

#### 7. User Interface
- **No Real-time Dashboard Updates**: Dashboard requires manual refresh
- **No Pagination**: History page loads all records (performance issue with large datasets)
- **Limited Export Options**: No Excel or custom format export
- **No Date Range Validation**: Can select invalid date ranges

#### 8. System Architecture
- **No Authentication**: Open access to all endpoints
- **No Rate Limiting**: Vulnerable to abuse
- **No Multi-tenancy**: Single user/organization only
- **No Backup Strategy**: No automated database backups

---

### Known Issues

#### Issue 1: MJPEG Stream Disconnects
**Description**: Live preview streams occasionally disconnect without error
**Workaround**: Refresh page or restart stream
**Planned Fix**: Implement automatic reconnection in frontend

#### Issue 2: Memory Leak in Long CCTV Streams
**Description**: Memory usage gradually increases during extended CCTV streaming
**Workaround**: Restart stream periodically
**Planned Fix**: Improve memory management in tracking dictionary

#### Issue 3: Timezone Handling
**Description**: All timestamps stored in server local time, not UTC
**Impact**: Issues in multi-timezone deployments
**Planned Fix**: Migrate to UTC storage with timezone conversion

#### Issue 4: Video Codec Compatibility
**Description**: Some browsers cannot play MP4V-encoded videos
**Workaround**: Download and play in VLC
**Planned Fix**: Add H.264 codec support (requires additional dependencies)

#### Issue 5: Concurrent Job Limit
**Description**: No enforcement of concurrent video processing limit
**Impact**: System may run out of resources with many simultaneous uploads
**Planned Fix**: Implement job queue with max concurrent workers

#### Issue 6: Export Timeout
**Description**: Exporting very large datasets times out
**Workaround**: Reduce date range or limit
**Planned Fix**: Implement chunked export with progress indicator

---

### Platform-Specific Issues

#### Windows
- **Path Issues**: Backslash vs. forward slash in file paths
- **Port Conflicts**: Port 8000 often used by other applications
- **VideoCapture Backend**: Some video codecs not supported

#### Linux
- **OpenCV Dependencies**: May require additional system packages (`libgl1`)
- **File Permissions**: Ensure correct permissions for database and log directories

#### macOS
- **OpenCV Webcam Access**: Requires camera permissions
- **Port Binding**: May require sudo for ports below 1024

---

## 15. Future Improvements

### Short-term Improvements (Next Release)

#### 1. Enhanced Detection
- **Multi-Class Support**: Detect cars, bikes, buses, etc.
- **Direction Indicators**: Arrow overlays showing movement direction
- **Confidence Threshold Adjustment**: UI control to adjust detection sensitivity
- **Batch Image Processing**: Upload and process multiple images at once

#### 2. Advanced Counting
- **Multiple Counting Lines**: Support for multiple entry/exit points
- **Zone-Based Counting**: Count vehicles in specific zones (parking, waiting area)
- **Directional Lines**: Separate lines for entry and exit
- **Manual Count Correction**: Allow users to adjust counts if needed

#### 3. User Interface Enhancements
- **Real-time Dashboard**: WebSocket-based live updates
- **Pagination**: Paginate history and logs tables
- **Advanced Filters**: More filter options (time ranges, confidence levels)
- **Customizable Themes**: Dark mode support
- **Mobile Responsiveness**: Better mobile and tablet support

#### 4. Export and Reporting
- **Excel Export**: Add .xlsx export format
- **Custom PDF Reports**: Branded PDF reports with charts
- **Scheduled Reports**: Automatic daily/weekly report generation
- **Email Notifications**: Send reports via email

#### 5. System Improvements
- **User Authentication**: JWT-based login system
- **Role-Based Access Control**: Admin, Operator, Viewer roles
- **Audit Logs**: Track all user actions
- **API Rate Limiting**: Prevent abuse
- **Database Backup**: Automated backup to cloud storage

---

### Medium-term Improvements

#### 1. Advanced Analytics
- **Machine Learning Insights**: Predict peak hours, traffic patterns
- **Anomaly Detection**: Detect unusual traffic patterns
- **Heatmap Generation**: Visualize traffic density
- **Comparison Reports**: Compare traffic across cameras or time periods

#### 2. Camera Management
- **Camera Groups**: Organize cameras into logical groups
- **Camera Configuration**: Store line positions per camera
- **Health Monitoring**: Alert when cameras go offline
- **PTZ Control**: Control pan-tilt-zoom cameras

#### 3. Integration Features
- **Webhook Support**: Send events to external systems
- **API Webhooks**: Notify on entry/exit events
- **Third-party Integration**: Integrate with access control systems
- **Database Options**: Support PostgreSQL, MySQL

#### 4. Performance Enhancements
- **GPU Acceleration**: Full CUDA support for faster inference
- **Distributed Processing**: Process videos across multiple workers
- **Caching Layer**: Redis cache for frequently accessed data
- **CDN Integration**: Serve processed videos via CDN

#### 5. Video Processing
- **H.264 Encoding**: Better video codec support
- **Custom Resolution**: Choose output video resolution
- **Trimming**: Process only specific time ranges
- **Replay Feature**: Replay historical streams with annotations

---

### Long-term Vision

#### 1. Cloud-Native Architecture
- **Microservices**: Split into separate services (detection, analytics, API)
- **Container Orchestration**: Kubernetes deployment
- **Auto-scaling**: Scale based on load
- **Multi-region**: Deploy across multiple regions

#### 2. Advanced AI Features
- **Vehicle Re-identification**: Track same vehicle across multiple cameras
- **License Plate Recognition**: Read and store plate numbers
- **Behavior Analysis**: Detect suspicious behavior (loitering, U-turns)
- **Crowd Counting**: Estimate crowd density
- **Face Blurring**: Privacy protection by blurring faces

#### 3. Enterprise Features
- **Multi-tenancy**: Support multiple organizations
- **White-labeling**: Customize branding per client
- **SLA Monitoring**: Track uptime and performance
- **Compliance**: GDPR, HIPAA compliance features

#### 4. Mobile Applications
- **iOS App**: Native iPhone/iPad application
- **Android App**: Native Android application
- **Push Notifications**: Real-time alerts on mobile
- **Offline Mode**: View cached data without internet

#### 5. Edge Computing
- **Edge Deployment**: Run detection on edge devices (Jetson Nano, Coral)
- **Federated Learning**: Train models across edge devices
- **Local Processing**: Reduce bandwidth by processing at source

---

### Community and Open Source

#### Potential Contributions
- **Model Zoo**: Share trained models for different vehicle types
- **Plugin System**: Allow community plugins for custom features
- **Translation**: Multi-language support
- **Documentation**: Expand documentation with tutorials and guides
- **Testing**: Comprehensive test suite (unit, integration, E2E)

---

## Conclusion

This Smart Rickshaw Entry-Exit Monitoring System is a comprehensive solution combining modern web technologies, computer vision, and AI to provide automated vehicle monitoring and analytics. The modular architecture allows for easy extension and customization to meet specific requirements.

**Key Strengths**:
- Production-ready FastAPI backend with robust error handling
- Modern React frontend with intuitive UI
- Real-time processing with live preview capabilities
- Comprehensive analytics and reporting
- Well-documented codebase

**Recommended Next Steps**:
1. Implement authentication and authorization
2. Add pagination to history tables
3. Enhance mobile responsiveness
4. Implement automated testing
5. Add multi-camera zone management

For questions, issues, or contributions, please refer to the project repository or contact the development team.

---

**Document Version**: 1.0  
**Last Updated**: January 26, 2026  
**Project Version**: 2.0.0
