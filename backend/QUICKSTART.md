# Rickshaw Detection API - Quick Start Guide

## Setup and Run (5 minutes)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python app/main.py
```

Or with uvicorn:
```bash
python -m uvicorn app.main:app --reload
```

### 3. Access the API
- **API Docs**: http://localhost:8000/docs
- **API Root**: http://localhost:8000

## Test the API

### Using Swagger UI (Easiest)
1. Open http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Upload a file and click "Execute"

### Using curl

**Image Detection:**
```bash
curl -X POST "http://localhost:8000/api/detect/image" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg"
```

**Video Detection:**
```bash
curl -X POST "http://localhost:8000/api/detect/video" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/video.mp4"
```

**Get History:**
```bash
curl -X GET "http://localhost:8000/api/history"
```

### Using Python requests
```python
import requests

# Image detection
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/detect/image',
        files={'file': f}
    )
    print(response.json())

# Get history
response = requests.get('http://localhost:8000/api/history')
print(response.json())
```

## Architecture Overview

### Request Flow
```
1. Client uploads file → 
2. Route validates file → 
3. Service processes with YOLO → 
4. Utils draw bounding boxes → 
5. File saved to outputs/ → 
6. Record saved to database → 
7. Response with URL
```

### Key Components
- **main.py**: Application entry point, route registration
- **core/startup.py**: Loads YOLO model ONCE at startup
- **routes/**: API endpoint handlers
- **services/**: Business logic (image/video processing)
- **model/detector.py**: YOLO wrapper
- **utils/**: Helper functions (file ops, drawing)
- **db/**: Database operations and schemas

## Configuration

Edit `app/core/config.py`:

```python
# Use GPU if available
yolo_device: str = "cuda"  # or "cpu"

# Detection thresholds
yolo_confidence: float = 0.25  # Lower = more detections
yolo_iou: float = 0.45

# File size limits
max_upload_size: int = 500 * 1024 * 1024  # 500 MB
```

## Troubleshooting

### "Model not found" error
```bash
# Ensure best.pt is in the right place
ls backend/app/model/best.pt
```

### Port 8000 already in use
```bash
# Use a different port
python -m uvicorn app.main:app --port 8001
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. ✅ Test image detection with a sample image
2. ✅ Test video detection with a sample video
3. ✅ Check detection history
4. ✅ View processed files at `/outputs/images/` or `/outputs/videos/`
5. 🚀 Integrate with your frontend!

## API Response Examples

**Successful Image Detection:**
```json
{
  "success": true,
  "file_name": "a1b2c3d4.jpg",
  "rickshaw_count": 3,
  "output_url": "/outputs/images/a1b2c3d4.jpg",
  "message": "Image processed successfully"
}
```

**Detection History:**
```json
{
  "success": true,
  "total_records": 5,
  "detections": [
    {
      "id": 5,
      "file_type": "video",
      "file_name": "xyz789.mp4",
      "rickshaw_count": 7,
      "created_at": "2025-12-26 14:30:15"
    }
  ]
}
```

Happy coding! 🚀
