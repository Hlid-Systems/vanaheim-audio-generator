from app.infrastructure.api.main import app

# This file remains as the entry point for Uvicorn/Docker
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)