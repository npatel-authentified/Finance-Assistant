#!/usr/bin/env python
"""
Launcher script for AI Finance Assistant Web UI.

Usage:
    python run_webapp.py
    uv run python run_webapp.py
"""

import sys
from pathlib import Path
import subprocess

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import gradio
except ImportError:
    print("=" * 70)
    print("⚠️  Gradio not installed")
    print("=" * 70)
    print()
    print("Installing Gradio...")
    print()

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio"])
        print()
        print("✅ Gradio installed successfully!")
        print()
    except subprocess.CalledProcessError:
        print()
        print("❌ Failed to install Gradio")
        print()
        print("Please install manually:")
        print("  uv pip install gradio")
        print("  # or")
        print("  pip install gradio")
        print()
        sys.exit(1)

# Import and run the app
from web_app.app import demo

if __name__ == "__main__":
    demo.launch()
