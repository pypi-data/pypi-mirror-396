import os
import signal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with status dashboard and chat interface"""
    b = get_backend()
    status_color = "#4caf50" if b else "#f44336"
    status_text = "Online" if b else "Offline (No Backend)"
    backend_name = b.backend_name() if b else "None"
    
    return f"""
    <html>
        <head>
            <title>lmapp Server</title>
            <style>
                body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; background: #1e1e1e; color: #e0e0e0; }}
                .card {{ background: #2d2d2d; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 2rem; }}
                h1 {{ color: #4ec9b0; margin-top: 0; }}
                .status {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; background: {status_color}; color: white; font-weight: bold; font-size: 0.875rem; }}
                .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem; }}
                .info-item {{ background: #333; padding: 1rem; border-radius: 6px; }}
                .label {{ display: block; color: #888; font-size: 0.875rem; margin-bottom: 0.5rem; }}
                .value {{ font-size: 1.125rem; font-weight: 500; }}
                code {{ background: #111; padding: 0.2rem 0.4rem; border-radius: 4px; font-family: monospace; }}
                
                /* Chat Interface */
                .chat-container {{ display: flex; flex-direction: column; height: 400px; border: 1px solid #444; border-radius: 6px; background: #111; }}
                .chat-messages {{ flex: 1; overflow-y: auto; padding: 1rem; }}
                .message {{ margin-bottom: 1rem; padding: 0.5rem 1rem; border-radius: 4px; max-width: 80%; }}
                .user {{ background: #264f78; align-self: flex-end; margin-left: auto; }}
                .assistant {{ background: #333; align-self: flex-start; margin-right: auto; }}
                .input-area {{ display: flex; padding: 1rem; border-top: 1px solid #444; background: #2d2d2d; }}
                input {{ flex: 1; padding: 0.5rem; border-radius: 4px; border: 1px solid #444; background: #1e1e1e; color: white; margin-right: 0.5rem; }}
                button {{ padding: 0.5rem 1rem; border-radius: 4px; border: none; cursor: pointer; font-weight: bold; }}
                .send-btn {{ background: #4ec9b0; color: #1e1e1e; }}
                .shutdown-btn {{ background: #f44336; color: white; margin-left: auto; }}
                
                .header-actions {{ display: flex; align-items: center; gap: 1rem; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="header-actions">
                        <h1>lmapp Server</h1>
                        <span class="status">{status_text}</span>
                    </div>
                    <button onclick="shutdownServer()" class="shutdown-btn">Shutdown Server</button>
                </div>
                <p>Local LLM API Server is running and ready for VS Code integration.</p>
                
                <div class="info-grid">
                    <div class="info-item">
                        <span class="label">Version</span>
                        <span class="value">{__version__}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Active Backend</span>
                        <span class="value">{backend_name}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">API Endpoint</span>
                        <span class="value"><code>/v1/completions</code></span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Chat Terminal</h2>
                <div class="chat-container">
                    <div id="messages" class="chat-messages">
                        <div class="message assistant">Hello! I'm your local AI assistant. How can I help you?</div>
                    </div>
                    <div class="input-area">
                        <input type="text" id="userInput" placeholder="Type a message..." onkeypress="handleKeyPress(event)">
                        <button onclick="sendMessage()" class="send-btn">Send</button>
                    </div>
                </div>
            </div>

            <script>
                async function shutdownServer() {{
                    if (confirm('Are you sure you want to shut down the server?')) {{
                        try {{
                            await fetch('/admin/shutdown', {{ method: 'POST' }});
                            document.body.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:100vh;color:#f44336"><h1>Server Shut Down</h1></div>';
                        }} catch (e) {{
                            alert('Failed to shutdown: ' + e);
                        }}
                    }}
                }}

                function handleKeyPress(e) {{
                    if (e.key === 'Enter') sendMessage();
                }}

                async function sendMessage() {{
                    const input = document.getElementById('userInput');
                    const text = input.value.trim();
                    if (!text) return;

                    // Add user message
                    addMessage(text, 'user');
                    input.value = '';
                    input.disabled = true;

                    try {{
                        const response = await fetch('/v1/completions', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                model: 'tinyllama',
                                prompt: text,
                                max_tokens: 200
                            }})
                        }});
                        
                        const data = await response.json();
                        if (data.choices && data.choices.length > 0) {{
                            addMessage(data.choices[0].text, 'assistant');
                        }}
                    }} catch (e) {{
                        addMessage('Error: ' + e.message, 'assistant');
                    }} finally {{
                        input.disabled = false;
                        input.focus();
                    }}
                }}

                function addMessage(text, sender) {{
                    const div = document.createElement('div');
                    div.className = `message ${{sender}}`;
                    div.textContent = text;
                    const container = document.getElementById('messages');
                    container.appendChild(div);
                    container.scrollTop = container.scrollHeight;
                }}
            </script>
        </body>
    </html>
    """


@app.post("/admin/shutdown")
def shutdown_server(request: Request):
    """Shutdown the server"""
    if request.client.host != "127.0.0.1":
        logger.warning(f"Unauthorized shutdown attempt from {request.client.host}")
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    logger.info("Shutdown requested via API")
    # Schedule shutdown
    os.kill(os.getpid(), signal.SIGINT)
    return {"status": "shutting_down"}


@app.get("/health", response_model=HealthResponse)
def health_check():
    b = get_backend()
    status = "ok" if b else "no_backend"
    backend_name = b.backend_name() if b else None
    models = b.list_models() if b else []

    return HealthResponse(
        status=status, version=__version__, backend=backend_name, models=models
    )


@app.post("/v1/completions", response_model=CompletionResponse)
def create_completion(request: CompletionRequest):
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
