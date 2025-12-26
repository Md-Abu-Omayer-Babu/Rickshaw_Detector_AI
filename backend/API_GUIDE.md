# API Quick Reference Guide

## Base URL
```
http://localhost:8000
```

## Quick Start

### 1. Start the Server
```bash
cd backend
python app/main.py
```

### 2. Test Image Detection
```bash
curl -X POST "http://localhost:8000/api/detect/image" \
  -F "file=@test_image.jpg"
```

### 3. Test Video with Counting
```bash
curl -X POST "http://localhost:8000/api/detect/video?enable_counting=true" \
  -F "file=@test_video.mp4"
```

### 4. View Dashboard
```bash
curl "http://localhost:8000/api/analytics/dashboard"
```

## All Endpoints

### Detection APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/detect/image` | Detect rickshaws in image |
| POST | `/api/detect/video` | Process video with counting |
| POST | `/api/cctv/stream` | Process RTSP stream |
| POST | `/api/cctv/stream/test` | Test stream connection |

### Data APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/history` | Detection history |
| GET | `/api/logs` | Event logs with filters |
| GET | `/api/logs/stats` | Log statistics |

### Analytics APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Full dashboard |
| GET | `/api/analytics/daily` | Daily counts |
| GET | `/api/analytics/hourly` | Hourly distribution |
| GET | `/api/analytics/summary` | Quick summary |

### Export APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/logs` | Export logs (CSV/JSON) |
| GET | `/api/export/analytics` | Export analytics (CSV/JSON) |

## Common Request Examples

### CCTV Stream Processing
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

### Get Logs for Specific Date
```bash
curl "http://localhost:8000/api/logs?start_date=2024-01-01&end_date=2024-01-31&event_type=entry"
```

### Export Logs as CSV
```bash
curl "http://localhost:8000/api/export/logs?format=csv&start_date=2024-01-01" -o rickshaw_logs.csv
```

### Get Hourly Stats
```bash
curl "http://localhost:8000/api/analytics/hourly?date=2024-01-15"
```

## Response Examples

### Video Detection Response
```json
{
  "file_name": "output_20240115_143022.mp4",
  "rickshaw_count": 8,
  "total_entry": 12,
  "total_exit": 7,
  "net_count": 5,
  "output_url": "/outputs/output_20240115_143022.mp4"
}
```

### Dashboard Response
```json
{
  "total_entry": 450,
  "total_exit": 380,
  "net_count": 70,
  "today_entry": 35,
  "today_exit": 28,
  "today_net": 7,
  "peak_hour": {
    "hour": 14,
    "entry_count": 22,
    "exit_count": 15
  },
  "last_7_days": [...],
  "active_cameras": 3
}
```

### Logs Response
```json
{
  "total": 150,
  "count": 50,
  "offset": 0,
  "limit": 50,
  "logs": [
    {
      "id": 1,
      "timestamp": "2024-01-15T14:30:22",
      "event_type": "entry",
      "camera_id": "camera_01",
      "confidence": 0.92,
      "bbox_x1": 120,
      "bbox_y1": 250,
      "bbox_x2": 340,
      "bbox_y2": 480
    }
  ],
  "filters_applied": {
    "start_date": "2024-01-01"
  }
}
```

## Configuration

### Entry/Exit Line Configuration
Located in `app/core/config.py`:

```python
# Virtual line position (percentage of frame)
ENTRY_EXIT_LINE_X1_PERCENT = 0.3  # 30% from left edge
ENTRY_EXIT_LINE_Y1_PERCENT = 0.0  # Top of frame
ENTRY_EXIT_LINE_X2_PERCENT = 0.3  # 30% from left edge
ENTRY_EXIT_LINE_Y2_PERCENT = 1.0  # Bottom of frame

# Detection settings
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.4

# CCTV settings
MAX_CONCURRENT_STREAMS = 4
CCTV_RECONNECT_ATTEMPTS = 3
CCTV_FRAME_SKIP = 2
```

## Testing CCTV Streams

### Test with VLC First
```bash
vlc rtsp://your-camera-ip:554/stream
```

### Test Connection via API
```bash
curl -X POST "http://localhost:8000/api/cctv/stream/test" \
  -H "Content-Type: application/json" \
  -d '{"rtsp_url": "rtsp://192.168.1.100:554/stream1"}'
```

### Common RTSP URLs
- Generic: `rtsp://ip:554/stream`
- Hikvision: `rtsp://username:password@ip:554/Streaming/Channels/101`
- Dahua: `rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0`
- TP-Link: `rtsp://username:password@ip:554/stream1`

## Error Handling

### 400 Bad Request
- Invalid file format
- Invalid date format
- Missing required parameters

### 404 Not Found
- No data matching filters
- Endpoint not found

### 500 Internal Server Error
- Model loading failure
- Database error
- Processing error

## Database Queries

### View Recent Detections
```bash
sqlite3 database/detections.db "SELECT * FROM rickshaw_logs ORDER BY timestamp DESC LIMIT 10;"
```

### Get Today's Counts
```bash
sqlite3 database/detections.db "SELECT SUM(CASE WHEN event_type='entry' THEN 1 ELSE 0 END) as entries, SUM(CASE WHEN event_type='exit' THEN 1 ELSE 0 END) as exits FROM rickshaw_logs WHERE DATE(timestamp) = DATE('now');"
```

### Get Camera Statistics
```bash
sqlite3 database/detections.db "SELECT camera_id, COUNT(*) as events, SUM(CASE WHEN event_type='entry' THEN 1 ELSE 0 END) as entries FROM rickshaw_logs GROUP BY camera_id;"
```

## Performance Tips

1. **Video Processing**
   - Enable frame skipping: Set `CCTV_FRAME_SKIP = 3` or higher
   - Reduce resolution if input is high-res
   - Process shorter videos for testing

2. **CCTV Streams**
   - Limit concurrent streams: Set `MAX_CONCURRENT_STREAMS = 2`
   - Use lower quality stream if available
   - Increase frame skip for better performance

3. **Database**
   - Regular cleanup of old logs
   - Use date filters in queries
   - Export and archive old data

## Troubleshooting

### Model Not Found
```
Error: Cannot find model file at trained_model/best.pt
```
**Fix**: Ensure `best.pt` exists in `trained_model/` directory

### RTSP Connection Failed
```
Error: Failed to connect to RTSP stream
```
**Fix**: 
- Test with VLC first
- Check firewall settings
- Verify camera IP and port
- Check credentials if required

### Low FPS
```
Warning: Processing FPS is too low
```
**Fix**:
- Increase `CCTV_FRAME_SKIP`
- Enable GPU if available
- Reduce input resolution
- Process fewer streams concurrently

## Interactive Documentation

Visit these URLs when server is running:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API testing
  - Try out endpoints
  - See request/response schemas

- **ReDoc**: http://localhost:8000/redoc
  - Clean API documentation
  - Code examples
  - Download OpenAPI spec

## Development

### Run in Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG  # Linux/Mac
$env:LOG_LEVEL="DEBUG"  # Windows PowerShell

python app/main.py
```

### Check Logs
```bash
# View live logs
tail -f logs/app.log  # Linux/Mac
Get-Content logs/app.log -Wait  # Windows PowerShell

# Search for errors
grep ERROR logs/app.log  # Linux/Mac
Select-String -Pattern "ERROR" -Path logs/app.log  # Windows PowerShell
```

### Run Tests
```bash
# Test image endpoint
curl -X POST http://localhost:8000/api/detect/image -F "file=@test.jpg"

# Test health check
curl http://localhost:8000/health

# View all endpoints
curl http://localhost:8000/
```

## Support

- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Root**: http://localhost:8000/

---

For detailed information, see the full README.md file.
