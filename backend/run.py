"""
Simple run script for the Rickshaw Detection API.
Execute this file to start the server.
"""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  {settings.app_name:^55}  ║
    ║  {f'Version {settings.version}':^55}  ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Starting server...
    
    API Documentation:
    • Swagger UI: http://localhost:8000/docs
    • ReDoc:      http://localhost:8000/redoc
    
    API Endpoints:
    • POST /api/detect/image  - Detect rickshaws in images
    • POST /api/detect/video  - Detect rickshaws in videos
    • GET  /api/history       - View detection history
    
    Press CTRL+C to stop the server
    """)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
