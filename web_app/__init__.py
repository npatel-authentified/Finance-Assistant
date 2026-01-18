"""
Web UI for AI Finance Assistant.

A Gradio-based chat interface with real-time streaming.
"""

from .app import demo, get_app

__all__ = ["demo", "get_app"]
