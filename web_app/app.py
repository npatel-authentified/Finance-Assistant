"""
AI Finance Assistant - Web UI (Phase 1)

A Gradio-based chat interface for the AI Finance Assistant.
Shows real-time execution progress using LangGraph streaming.

Usage:
    python web_app/app.py
    # Or with uv:
    uv run python web_app/app.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import gradio as gr
import uuid
from typing import Generator, Tuple

# Import the LangGraph app
from src.orchestration import create_app_with_memory


# Global app instance
_app = None


def get_app():
    """Get or create the LangGraph app singleton."""
    global _app
    if _app is None:
        _app = create_app_with_memory()
    return _app


def format_status_update(node_name: str, state_update: dict) -> str:
    """Format execution progress for display."""
    if node_name == "fast_router":
        router_decision = state_update.get("router_decision")
        if router_decision:
            confidence = router_decision.confidence
            if router_decision.route == "direct":
                return f"🔍 Fast Router: Routing to **{router_decision.agent.value}** agent (confidence: {confidence:.2f})"
            else:
                return f"🔍 Fast Router: Using supervisor (low confidence: {confidence:.2f})"

    elif node_name == "supervisor":
        supervisor_decision = state_update.get("supervisor_decision")
        if supervisor_decision:
            primary = supervisor_decision.primary_agent.value
            if supervisor_decision.secondary_agents:
                secondary = [a.value for a in supervisor_decision.secondary_agents]
                return f"🎯 Supervisor: **{primary}** + {secondary} ({supervisor_decision.execution_mode})"
            else:
                return f"🎯 Supervisor: **{primary}** agent"

    elif node_name.endswith("_agent"):
        agent_name = node_name.replace("_agent", "")
        return f"▶️  Executing **{agent_name}** agent..."

    elif node_name == "sequence_router":
        return "➡️  Routing to next agent..."

    elif node_name == "synthesizer":
        return "📋 Synthesizing results from multiple agents..."

    return f"⚙️  {node_name}"


def chat_with_assistant(
    message: str,
    history: list,
    thread_id: str
) -> Generator[list, None, None]:
    """
    Chat with the AI Finance Assistant.

    Streams execution progress in real-time with typing indicator in chat.

    Args:
        message: User's question
        history: Chat history (list of message dicts)
        thread_id: Conversation thread ID

    Yields:
        Updated chat history with typing indicator and final response
    """
    if not message.strip():
        yield history
        return

    # Add user message to history (Gradio 6.x messages format)
    history = history + [{"role": "user", "content": message}]

    # Add typing indicator in chat (so user sees bot is working)
    typing_history = history + [{"role": "assistant", "content": "🤔 Thinking..."}]
    yield typing_history

    app = get_app()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Stream the workflow execution
        final_response = None

        # Send only the new message - LangGraph will merge with checkpointed history
        for chunk in app.stream(
            {
                "messages": [{"role": "user", "content": message}],
            },
            config,
            stream_mode="updates",
        ):
            # chunk is a dict with node name as key
            for node_name, state_update in chunk.items():
                # Format status update
                status = format_status_update(node_name, state_update)

                # Check for final response
                if "final_response" in state_update and state_update["final_response"]:
                    final_response = state_update["final_response"]

                # Update typing indicator with current progress
                typing_history = history + [{"role": "assistant", "content": f"⏳ {status}"}]
                yield typing_history

        # Get final response if not found in stream
        if not final_response:
            final_state = app.get_state(config)
            final_response = final_state.values.get("final_response", "No response generated")

        # Replace typing indicator with actual response
        history = history + [{"role": "assistant", "content": final_response}]
        yield history

    except Exception as e:
        error_response = f"I apologize, but I encountered an error: {str(e)}\n\nPlease try again or rephrase your question."
        # Replace typing indicator with error response
        history = history + [{"role": "assistant", "content": error_response}]
        yield history


def create_new_thread() -> str:
    """Create a new conversation thread ID."""
    return f"session_{uuid.uuid4().hex[:8]}"


def clear_chat() -> Tuple[list, str]:
    """Clear chat history and start new conversation."""
    new_thread = create_new_thread()
    return [], new_thread


# Create the Gradio interface
with gr.Blocks(title="AI Finance Assistant") as demo:
    # Header
    gr.Markdown(
        """
        # 🤖 AI Finance Assistant

        Ask questions about **finance, investments, portfolio analysis, and financial planning**.
 
        """
    )

    # Chat interface
    chatbot = gr.Chatbot(
        height=500,
        show_label=False,
    )

    # Status display
    # status_box = gr.Textbox(
    #     label="Status",
    #     value="Ready to answer your questions",
    #     interactive=False,
    #     show_label=True,
    # )

    # Input area
    with gr.Row():
        msg_input = gr.Textbox(
            placeholder="Ask a question about finance, investments, or your portfolio...",
            show_label=False,
            scale=4,
        )
        submit_btn = gr.Button("Send 📤", scale=1, variant="primary")

    # Thread ID display (hidden state)
    thread_id_state = gr.State(value=create_new_thread())

    # Controls
    with gr.Row():
        clear_btn = gr.Button("🗑️ Clear Chat", size="sm")
        # thread_display = gr.Textbox(
        #     label="Thread ID",
        #     interactive=False,
        #     scale=1,
        # )

    # Examples
    gr.Examples(
        examples=[
            "How is my portfolio performing?",
            "What is compound interest?",
            "Should I invest in Tesla?",
            "Help me plan for retirement",
            "What's happening in the market today?",
        ],
        inputs=msg_input,
        label="Example Questions",
    )

    # Event handlers
    msg_input.submit(
        chat_with_assistant,
        inputs=[msg_input, chatbot, thread_id_state],
        outputs=[chatbot],
    ).then(
        lambda: "",  # Clear input after submission
        outputs=[msg_input],
    )

    submit_btn.click(
        chat_with_assistant,
        inputs=[msg_input, chatbot, thread_id_state],
        outputs=[chatbot],
    ).then(
        lambda: "",  # Clear input after submission
        outputs=[msg_input],
    )

    clear_btn.click(
        clear_chat,
        outputs=[chatbot, thread_id_state],
    )

    # Update thread display when thread_id changes
    # thread_id_state.change(
    #     lambda x: x,
    #     inputs=[thread_id_state],
    #     outputs=[thread_display],
    # )

    # Initialize thread display
    # demo.load(
    #     lambda x: x,
    #     inputs=[thread_id_state],
    #     outputs=[thread_display],
    # )


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting AI Finance Assistant Web UI")
    print("=" * 70)
    print()
    print("Features:")
    print("  ✅ Real-time execution progress")
    print("  ✅ Multi-agent routing (Fast Router + Supervisor)")
    print("  ✅ Conversation persistence")
    print("  ✅ Clean, modern interface")
    print()
    print("=" * 70)
    print()

    # Launch the app
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set to True to create public link
        show_error=True,
        inbrowser=True,  # Auto-open browser
    )
