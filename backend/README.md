# Rickshaw Detection API

A production-ready FastAPI backend for detecting rickshaws in images and videos using YOLOv8.

## Features

- 🖼️ **Image Detection**: Upload images to detect and count rickshaws
- 🎥 **Video Detection**: Process videos frame-by-frame with real-time rickshaw counting
- 📊 **Detection History**: SQLite database storing all detection records
- 🎨 **Annotated Outputs**: Bounding boxes and labels on processed media
- 🚀 **Efficient Model Loading**: YOLO model loaded once at startup
- 📁 **Static File Serving**: Direct access to processed images and videos
- 📖 **Interactive API Docs**: Swagger UI and ReDoc

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **Ultralytics YOLO**: State-of-the-art object detection
- **OpenCV**: Video and image processing
- **SQLite3**: Lightweight database
- **Python 3.10+**: Required Python version

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   └── startup.py         # Startup/shutdown logic
│   ├── model/
│   │   ├── best.pt            # YOLO model weights
│   │   └── detector.py        # YOLO detector wrapper
│   ├── routes/
│   │   ├── detect_image.py    # Image detection endpoint
│   │   ├── detect_video.py    # Video detection endpoint
│   │   └── history.py         # History endpoint
│   ├── services/
│   │   ├── inference_service.py  # Image processing logic
│   │   └── video_service.py      # Video processing logic
│   ├── db/
│   │   ├── database.py        # Database operations
│   │   └── models.py          # Pydantic schemas
│   ├── utils/
│   │   ├── file_utils.py      # File handling utilities
│   │   └── draw_utils.py      # Drawing utilities
│   └── outputs/
│       ├── images/            # Processed images
│       └── videos/            # Processed videos
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.10 or higher
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
   Ensure `best.pt` exists in `app/model/` directory.

## Running the Application

### Development Mode

```bash
# From backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or run directly:

```bash
cd backend
python app/main.py
```

### Production Mode

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Image Detection

**POST** `/api/detect/image`

Upload an image to detect rickshaws.

**Request**:
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response**:
```json
{
  "success": true,
  "file_name": "abc123.jpg",
  "rickshaw_count": 5,
  "output_url": "/outputs/images/abc123.jpg",
  "message": "Image processed successfully"
}
```

**Supported formats**: JPG, JPEG, PNG, BMP, WEBP

### 2. Video Detection

**POST** `/api/detect/video`

Upload a video to detect rickshaws frame by frame.

**Request**:
- Content-Type: `multipart/form-data`
- Body: `file` (video file)

**Response**:
```json
{
  "success": true,
  "file_name": "def456.mp4",
  "rickshaw_count": 8,
  "output_url": "/outputs/videos/def456.mp4",
  "message": "Video processed successfully"
}
```

**Supported formats**: MP4, AVI, MOV, MKV

### 3. Detection History

**GET** `/api/history`

Retrieve all detection records.

**Response**:
```json
{
  "success": true,
  "total_records": 10,
  "detections": [
    {
      "id": 1,
      "file_type": "image",
      "file_name": "abc123.jpg",
      "rickshaw_count": 5,
      "created_at": "2025-12-26 10:30:00"
    }
  ]
}
```

## Configuration

Edit `app/core/config.py` to customize:

- **Upload limits**: Maximum file size
- **Model settings**: Confidence threshold, IoU threshold
- **Device**: CPU or CUDA (GPU)
- **CORS settings**: Allowed origins
- **File paths**: Output directories

## Database

SQLite database (`detections.db`) stores:
- Detection ID
- File type (image/video)
- File name
- Rickshaw count
- Timestamp

Schema is created automatically on first run.

## Error Handling

All endpoints return proper HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid file format)
- `422`: Validation error
- `500`: Internal server error

Error response format:
```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed information"
}
```

## Testing with curl

### Image Detection
```bash
curl -X POST "http://localhost:8000/api/detect/image" \
  -F "file=@path/to/image.jpg"
```

### Video Detection
```bash
curl -X POST "http://localhost:8000/api/detect/video" \
  -F "file=@path/to/video.mp4"
```

### Get History
```bash
curl "http://localhost:8000/api/history"
```

## Performance Tips

1. **Use GPU**: Change `yolo_device` to `"cuda"` in config.py if NVIDIA GPU available
2. **Adjust confidence**: Lower threshold detects more objects but may include false positives
3. **Video processing**: Large videos take time; consider frame skipping for faster processing
4. **Production deployment**: Use multiple workers with Gunicorn

## Troubleshooting

### Model not found
Ensure `best.pt` is in `app/model/` directory.

### CUDA errors
If GPU not available, ensure `yolo_device = "cpu"` in config.py.

### Import errors
Verify all dependencies are installed: `pip install -r requirements.txt`

### Port already in use
Change port: `uvicorn app.main:app --port 8001`

## License

This project is for educational purposes.

## Support

For issues or questions, please contact the development team.
