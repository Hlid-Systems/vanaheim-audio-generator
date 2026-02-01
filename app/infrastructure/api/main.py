from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.api.v1.router import router as api_router
from app.infrastructure.config.settings import settings
from app.infrastructure.monitoring.logger import logger
from fastapi import Request
from fastapi.responses import JSONResponse
from app.domain.exceptions import VanaheimError, ResourceNotFoundError, ConfigurationError

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure directories exist
    logger.info("Vanaheim Service Starting...")
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.SCRIPTS_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    yield
    # Shutdown logic if needed
    logger.info("Vanaheim Service Shutting Down...")

# Swagger / OpenAPI Metadata
tags_metadata = [
    {
        "name": "Simulations",
        "description": "Core scenario-based audio generation (Corporate, Podcast, etc)."
    },
    {
        "name": "TTS",
        "description": "Simple direct Text-to-Speech operations."
    },
    {
        "name": "AI Tools",
        "description": "Developer tools using LLM prompts for script generation."
    }
]

app = FastAPI(
    title="Vanaheim Audio Generator",
    description=(
        "![Hexagonal](https://img.shields.io/badge/HEXAGONAL-ARCHITECTURE-2f3640?style=for-the-badge&logo=structure)  "
        "![FastAPI](https://img.shields.io/badge/FASTAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)  "
        "![Python](https://img.shields.io/badge/PYTHON-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)\n\n"
        "# Professional Audio Synthesis Service (V1)\n\n"
        "**Vanaheim** is the audio synthesis engine of **Hlid Systems**.\n\n"
        "It provides a robust, production-ready service for generating scenario-based audio simulations "
        "using multi-provider TTS (EdgeTTS) and LLM (OpenAI) orchestration.\n\n"
        "## Core Capabilities\n"
        "* **Free Mode** (`/tts/simple`): Simple TTS without API keys.\n"
        "* **Developer Mode** (`/ai/prompt`): Prompt-to-Audio with script generation.\n"
        "* **Scenario Mode** (`/simulation/scenario`): Complex multi-role simulations with timing control.\n"
        "* **Persistence**: Integration with Supabase (Munin) for auditing and storage."
    ),
    version="1.0.0",
    contact={
        "name": "Hlid Systems",
        "url": "https://github.com/Hlid-Systems",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

# Exception Handlers
@app.exception_handler(VanaheimError)
async def vanaheim_exception_handler(request: Request, exc: VanaheimError):
    logger.error(f"Domain Error: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={"status": "error", "message": exc.message, "type": "DomainError"},
    )

@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    logger.warning(f"Resource Not Found: {exc.message}")
    return JSONResponse(
        status_code=404,
        content={"status": "error", "message": exc.message, "type": "NotFound"},
    )

@app.exception_handler(ConfigurationError)
async def configuration_error_handler(request: Request, exc: ConfigurationError):
    logger.critical(f"Configuration Error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal Configuration Error", "type": "ConfigError"},
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Observability Middleware
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Inject Request ID
        request.state.request_id = request_id
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Add Headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

app.add_middleware(ObservabilityMiddleware)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Status"])
async def root():
    return {"message": "Vanaheim is running. Go to /docs for API."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.infrastructure.api.main:app", host="0.0.0.0", port=8000, reload=True)