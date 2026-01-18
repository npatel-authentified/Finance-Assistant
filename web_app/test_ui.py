"""
Test script for the Gradio UI.

This creates a minimal demo to verify Gradio is working,
without requiring full LangGraph dependencies.

Usage:
    python web_app/test_ui.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import gradio as gr
import time


def mock_chat(message: str, history: list):
    """Mock chat function for testing UI."""
    # Add user message (Gradio 6.x messages format)
    history = history + [{"role": "user", "content": message}]

    # Simulate processing
    yield history, "🔍 Fast Router: Analyzing question..."
    time.sleep(0.5)

    yield history, "▶️  Executing education agent..."
    time.sleep(0.5)

    # Generate mock response
    response = f"This is a test response to: '{message}'\n\nThe web UI is working correctly! ✅"
    history = history + [{"role": "assistant", "content": response}]

    yield history, "✅ Response complete"


def clear_chat():
    """Clear chat history."""
    return [], "🗑️  Chat cleared"


# Create minimal demo
with gr.Blocks(title="AI Finance Assistant - Test UI") as demo:
    gr.Markdown("# 🧪 AI Finance Assistant - UI Test")
    gr.Markdown("This is a test interface to verify Gradio is working.")

    chatbot = gr.Chatbot(height=400)
    status = gr.Textbox(label="Status", value="Ready", interactive=False)

    with gr.Row():
        msg = gr.Textbox(placeholder="Type a test message...", scale=4, show_label=False)
        submit = gr.Button("Send", scale=1, variant="primary")

    clear = gr.Button("Clear")

    # Event handlers
    msg.submit(mock_chat, [msg, chatbot], [chatbot, status]).then(
        lambda: "", outputs=[msg]
    )
    submit.click(mock_chat, [msg, chatbot], [chatbot, status]).then(
        lambda: "", outputs=[msg]
    )
    clear.click(clear_chat, outputs=[chatbot, status])


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 AI Finance Assistant - UI Test")
    print("=" * 70)
    print()
    print("This is a minimal test to verify Gradio is working.")
    print("The actual app is in web_app/app.py")
    print()
    print("=" * 70)
    print()

    demo.launch(server_port=7860)
