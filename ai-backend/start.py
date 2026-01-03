"""
Simple startup script to run the AI backend
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from config.settings import settings
    
    print("=" * 80)
    print("HCAT AI Backend - Starting...")
    print("=" * 80)
    print(f"Server: http://{settings.fastapi_host}:{settings.fastapi_port}")
    print(f"Backend URL: {settings.nestjs_backend_url}")
    print(f"Model: {settings.llm_model}")
    print("=" * 80)
    print("\nAPI Endpoints:")
    print(f"  - Health Check: http://localhost:{settings.fastapi_port}/health")
    print(f"  - Task Assignment: http://localhost:{settings.fastapi_port}/api/v1/decisions/task-assignment")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 80)
    
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=False,
        log_level="debug"
    )
