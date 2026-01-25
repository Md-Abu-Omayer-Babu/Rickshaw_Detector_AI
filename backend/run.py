import uvicorn
from app.core.config import settings, logger

if __name__ == "__main__":
    print(f"""
    {settings.app_name:^55}  
    {f'Version {settings.version}':^55}
    
    Starting server...
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
