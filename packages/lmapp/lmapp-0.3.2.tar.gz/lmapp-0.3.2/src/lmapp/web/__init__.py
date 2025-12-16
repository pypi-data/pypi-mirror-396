"""
LMAPP Web UI Package.

Provides FastAPI-based self-hosted web interface for GitHub Copilot-style interaction.

Features:
- REST API for chat, documents, models, and plugins
- WebSocket support for streaming chat
- Static file serving (HTML/CSS/JavaScript)
- CORS support for development

Author: LMAPP Community
License: MIT
"""

__version__ = "0.2.6"
__all__ = ["server"]
