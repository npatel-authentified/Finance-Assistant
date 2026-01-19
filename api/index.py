"""
Vercel Serverless Entry Point for AI Finance Assistant

This file serves as the bridge between Vercel's serverless platform
and the Gradio application.
"""

import sys
from pathlib import Path

# Add project root to Python path so imports work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import gradio as gr

# Import the Gradio demo from web_app
from web_app.app import demo

# Create FastAPI app
app = FastAPI(title="AI Finance Assistant")

# Redirect root to the Gradio app
@app.get("/")
async def root():
    """Redirect root to Gradio interface."""
    return RedirectResponse(url="/gradio")

# Mount Gradio app at /gradio path
app = gr.mount_gradio_app(app, demo, path="/gradio")

# Vercel handler - this is what Vercel calls
handler = app
