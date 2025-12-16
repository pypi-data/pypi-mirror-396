"""
LMAPP Web UI Server - FastAPI backend for GitHub Copilot-style interface.

Serves static files and provides REST API + WebSocket for real-time chat,
document management, and plugin integration.

Author: LMAPP Community
License: MIT
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LMAPP Web UI",
    description="Self-hosted GitHub Copilot-style interface for offline AI",
    version="0.2.6",
)

# Add CORS middleware for localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request validation
class ChatMessage(BaseModel):
    """Chat message request."""

    message: str
    model: Optional[str] = None


class DocumentUpload(BaseModel):
    """Document upload metadata."""

    filename: str
    size: int


class PluginInstallRequest(BaseModel):
    """Plugin installation request."""

    plugin_name: str


# In-memory storage (would be replaced with persistent storage in production)
class AppState:
    """Application state."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.chat_history: List[Dict[str, str]] = []
        self.uploaded_documents: Dict[str, Dict[str, Any]] = {}
        self.installed_plugins: List[str] = []


state = AppState()


# Routes


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main HTML page."""
    static_dir = Path(__file__).parent / "static"
    html_file = static_dir / "index.html"

    if html_file.exists():
        return FileResponse(html_file)

    # Fallback if file doesn't exist yet - return simple HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>LMAPP Web UI</title></head>
    <body>
        <h1>LMAPP Web UI Server Running</h1>
        <p>Version: 0.2.6</p>
        <p>Status: Ready</p>
    </body>
    </html>
    """
    return html_content


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "LMAPP Web UI",
        "version": "0.2.6",
    }


@app.get("/api/models")
async def get_models():
    """Get available LLM models."""
    # This would integrate with BackendDetector in real implementation
    return {
        "success": True,
        "models": ["ollama-default", "neural-chat", "mistral"],
        "default_model": "ollama-default",
        "status": "available",
    }


@app.post("/api/chat")
async def chat(request: ChatMessage):
    """Send a chat message (non-streaming)."""
    if not request.message:
        raise HTTPException(status_code=400, detail="Message required")

    message = request.message
    model = request.model or "ollama-default"

    # Store in history
    state.chat_history.append(
        {
            "role": "user",
            "content": message,
            "model": model,
        }
    )

    # This would integrate with ChatSession in real implementation
    response = f"Response from {model} to: {message[:50]}..."

    state.chat_history.append(
        {
            "role": "assistant",
            "content": response,
            "model": model,
        }
    )

    return {
        "success": True,
        "message": message,
        "response": response,
        "model": model,
    }


@app.get("/api/documents")
async def list_documents():
    """Get uploaded documents."""
    documents = [
        {
            "id": doc_id,
            "name": doc_meta["filename"],
            "size": doc_meta["size"],
            "chunks": doc_meta.get("chunks", 0),
            "indexed": True,
        }
        for doc_id, doc_meta in state.uploaded_documents.items()
    ]

    return {
        "success": True,
        "documents": documents,
        "total_documents": len(documents),
        "total_size": sum(d["size"] for d in documents),
    }


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for RAG indexing."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    # In real implementation, would save file and index with RAGSystem
    doc_id = f"doc_{len(state.uploaded_documents) + 1}"

    state.uploaded_documents[doc_id] = {
        "filename": file.filename,
        "size": file.size or 0,
        "chunks": 0,
    }

    return {
        "success": True,
        "document_id": doc_id,
        "filename": file.filename,
        "message": "Document uploaded successfully",
    }


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the knowledge base."""
    if doc_id not in state.uploaded_documents:
        raise HTTPException(status_code=404, detail="Document not found")

    del state.uploaded_documents[doc_id]

    return {
        "success": True,
        "message": f"Document {doc_id} deleted",
    }


@app.get("/api/plugins")
async def list_plugins():
    """Get available plugins."""
    # This would integrate with PluginManager in real implementation
    available_plugins = [
        {
            "name": "translator",
            "version": "0.1.0",
            "author": "community",
            "description": "Multi-language translation",
            "installed": "translator" in state.installed_plugins,
            "tags": ["translation", "language"],
        },
        {
            "name": "code-analyzer",
            "version": "0.1.0",
            "author": "community",
            "description": "Static code analysis",
            "installed": "code-analyzer" in state.installed_plugins,
            "tags": ["code", "analysis"],
        },
        {
            "name": "code-refactoring",
            "version": "0.1.0",
            "author": "community",
            "description": "Code pattern analysis and refactoring suggestions",
            "installed": "code-refactoring" in state.installed_plugins,
            "tags": ["refactoring", "analysis"],
        },
        {
            "name": "knowledge-base",
            "version": "0.1.0",
            "author": "community",
            "description": "Personal knowledge management",
            "installed": "knowledge-base" in state.installed_plugins,
            "tags": ["knowledge", "search"],
        },
    ]

    return {
        "success": True,
        "plugins": available_plugins,
        "total": len(available_plugins),
        "installed": len(state.installed_plugins),
    }


@app.post("/api/plugins/{plugin_name}/install")
async def install_plugin(plugin_name: str):
    """Install a plugin."""
    if plugin_name in state.installed_plugins:
        return {
            "success": False,
            "error": f"Plugin {plugin_name} already installed",
        }

    state.installed_plugins.append(plugin_name)

    return {
        "success": True,
        "plugin": plugin_name,
        "message": f"Plugin {plugin_name} installed successfully",
    }


@app.post("/api/plugins/{plugin_name}/uninstall")
async def uninstall_plugin(plugin_name: str):
    """Uninstall a plugin."""
    if plugin_name not in state.installed_plugins:
        raise HTTPException(status_code=404, detail="Plugin not installed")

    state.installed_plugins.remove(plugin_name)

    return {
        "success": True,
        "plugin": plugin_name,
        "message": f"Plugin {plugin_name} uninstalled successfully",
    }


@app.get("/api/status")
async def status():
    """Get system status."""
    return {
        "success": True,
        "server": "LMAPP Web UI",
        "version": "0.2.6",
        "status": "running",
        "features": {
            "chat": True,
            "documents": True,
            "plugins": True,
            "websocket": True,
        },
        "stats": {
            "documents": len(state.uploaded_documents),
            "chat_messages": len(state.chat_history),
            "plugins_installed": len(state.installed_plugins),
        },
    }


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat."""
    await websocket.accept()
    state.active_connections.append(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message = message_data.get("message", "")
            model = message_data.get("model", "ollama-default")

            if not message:
                await websocket.send_json(
                    {
                        "error": "Message required",
                    }
                )
                continue

            # Store in history
            state.chat_history.append(
                {
                    "role": "user",
                    "content": message,
                }
            )

            # Simulate streaming response
            response = f"Streaming response from {model} to: {message}"

            # Send response token by token (simulated)
            for token in response.split():
                await websocket.send_json(
                    {
                        "type": "token",
                        "content": token + " ",
                        "model": model,
                    }
                )

            # Send completion marker
            await websocket.send_json(
                {
                    "type": "complete",
                    "message": message,
                    "full_response": response,
                }
            )

            # Store in history
            state.chat_history.append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        state.active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        state.active_connections.remove(websocket)


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


# Startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("LMAPP Web UI Server starting...")
    logger.info("Listening on http://localhost:5000")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("LMAPP Web UI Server shutting down...")


# Mount static files (if they exist)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
        log_level="info",
    )
