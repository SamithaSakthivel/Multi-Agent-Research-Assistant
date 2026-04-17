import uvicorn

if __name__ == "__main__":
    # Import the combined FastAPI + Socket.IO app
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,          # auto-reload on file changes during dev
        log_level="info",
    )
