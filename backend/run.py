"""
Run script for the Smart Rickshaw Entry-Exit Monitoring System.
Execute this file to start the FastAPI server with all features enabled.
"""
import uvicorn
from app.core.config import settings, logger

if __name__ == "__main__":
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  {settings.app_name:^55}  ║
    ║  {f'Version {settings.version}':^55}  ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Starting server...
    
    📚 API Documentation:
    • Swagger UI: http://localhost:8000/docs
    • ReDoc:      http://localhost:8000/redoc
    • Health:     http://localhost:8000/health
    
    🎯 Detection Endpoints:
    • POST /api/detect/image        - Detect rickshaws in images
    • POST /api/detect/video        - Detect with entry/exit counting
    • POST /api/cctv/stream         - Process RTSP/CCTV streams
    • POST /api/cctv/stream/test    - Test CCTV connection
    
    📊 Data & Analytics:
    • GET  /api/history             - Detection history
    • GET  /api/logs                - Entry/exit event logs
    • GET  /api/analytics/dashboard - Analytics dashboard
    • GET  /api/analytics/daily     - Daily statistics
    • GET  /api/analytics/hourly    - Hourly distribution
    
    💾 Export:
    • GET  /api/export/logs         - Export logs (CSV/JSON)
    • GET  /api/export/analytics    - Export analytics (CSV/JSON)
    
    ⚙️  Configuration:
    • Model: {settings.model_path}
    • Device: {settings.yolo_device.upper()}
    • Debug Mode: {'ON' if settings.debug else 'OFF'}
    • Max Streams: {settings.max_concurrent_streams}
    
    📝 Logs: {settings.logs_dir / settings.log_file}
    
    Press CTRL+C to stop the server
    """)
    
    logger.info("Starting Rickshaw Detection API Server")
    logger.info(f"Server configuration: host=0.0.0.0, port=8000, reload={settings.debug}")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
