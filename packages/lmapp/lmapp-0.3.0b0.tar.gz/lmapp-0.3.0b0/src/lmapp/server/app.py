from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time

from lmapp import __version__
from lmapp.backend.detector import BackendDetector
from lmapp.utils.logging import logger

app = FastAPI(
    title="lmapp API",
    description="Local LLM API Server for VS Code Integration",
    version=__version__,
)

# --- Models ---


class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7
    stop: Optional[List[str]] = None


class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    version: str
    backend: Optional[str]
    models: List[str]


# --- State ---

backend = None


def get_backend():
    global backend
    if backend and backend.is_running():
        return backend

    detector = BackendDetector()
    # Try to find running backend first
    for b in detector.detect_all():
        if b.is_running():
            backend = b
            return backend

    # If none running, try to start one?
    # For now, just return None if nothing is running
    return None


# --- Endpoints ---


@app.get("/health", response_model=HealthResponse)
async def health_check():
    b = get_backend()
    status = "ok" if b else "no_backend"
    backend_name = b.backend_name() if b else None
    models = b.list_models() if b else []

    return HealthResponse(
        status=status, version=__version__, backend=backend_name, models=models
    )


@app.post("/v1/completions", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest):
    b = get_backend()
    if not b:
        raise HTTPException(status_code=503, detail="No LLM backend available")

    try:
        # This is a simplified chat call for now.
        # Real FIM (Fill-In-Middle) requires specific model support.
        # We'll treat the prompt as a user message.
        response_text = b.chat(request.prompt, model=request.model)

        return CompletionResponse(
            id=f"cmpl-{int(time.time())}",
            created=int(time.time()),
            model=request.model,
            choices=[
                {
                    "text": response_text,
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop",
                }
            ],
        )
    except Exception as e:
        logger.error(f"Completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
