# AI Finance Assistant - Web UI

A clean, modern chat interface for the AI Finance Assistant built with Gradio.

## Features

✅ **Real-time Streaming** - See execution progress as agents work
✅ **Multi-Agent Routing** - Automatic routing to specialized agents
✅ **Conversation Persistence** - Thread-based conversation memory
✅ **Clean Interface** - Professional, easy-to-use UI
✅ **Example Questions** - Quick start prompts

## Quick Start

### 1. Install Gradio

```bash
uv pip install gradio
```

### 2. Launch the App

```bash
# From project root
python web_app/app.py

# Or with uv
uv run python web_app/app.py
```

### 3. Open Browser

The app will open automatically at: **http://localhost:7860**

## Usage

### Ask Questions

Simply type your question in the input box:

- "How is my portfolio performing?"
- "What is compound interest?"
- "Should I invest in Tesla?"
- "Help me plan for retirement"

### See Execution Progress

The status box shows real-time updates:

```
🔍 Fast Router: Routing to portfolio agent (confidence: 0.95)
▶️  Executing portfolio agent...
✅ Response complete
```

### Clear Chat

Click **"🗑️ Clear Chat"** to start a new conversation with a fresh thread.

## Interface Layout

```
┌──────────────────────────────────────────────────────┐
│  🤖 AI Finance Assistant                              │
├──────────────────────────────────────────────────────┤
│                                                       │
│  [Chat History]                                       │
│                                                       │
│  User: How is my portfolio?                          │
│  🤖: Your portfolio shows...                          │
│                                                       │
├──────────────────────────────────────────────────────┤
│  Status: ▶️ Executing portfolio agent...              │
├──────────────────────────────────────────────────────┤
│  [Ask a question...] [Send 📤]                        │
├──────────────────────────────────────────────────────┤
│  🗑️ Clear Chat    Thread ID: session_abc123          │
├──────────────────────────────────────────────────────┤
│  Example Questions:                                   │
│  • How is my portfolio performing?                    │
│  • What is compound interest?                         │
└──────────────────────────────────────────────────────┘
```

## Streaming Execution

The app uses LangGraph's streaming to show progress:

1. **Fast Router** - Pattern-based routing decision
2. **Supervisor** - LLM-based routing (if needed)
3. **Agent Execution** - Shows which agent is running
4. **Sequence Router** - Multi-agent coordination
5. **Synthesizer** - Combining results

## Configuration

### Port

Default: `7860`

Change in `app.py`:
```python
demo.launch(server_port=7860)
```

### Share Publicly

Create a public link (temporary):
```python
demo.launch(share=True)
```

### Authentication

Add basic auth:
```python
demo.launch(auth=("username", "password"))
```

## Architecture

```
web_app/app.py
    ↓
src.orchestration.create_app_with_memory()
    ↓
LangGraph StateGraph
    ↓
Fast Router → Supervisor → Agents → Synthesizer
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 7860
lsof -ti:7860 | xargs kill -9

# Or use different port
demo.launch(server_port=7861)
```

### Module Not Found

```bash
# Make sure you're in project root
cd /path/to/ai_finance_assistant

# Install dependencies
uv pip install gradio
```

### Agent Errors

Check the status box for error messages. Common issues:
- Missing API keys (OPENAI_API_KEY)
- Missing dependencies (pinecone, yfinance)

## Next Steps (Phase 2)

Phase 2 will add:
- 📊 Sidebar with agent information
- 📈 Usage statistics
- 🔀 Workflow visualization
- ⚙️ Settings panel
- 💾 Export conversations

## Development

### Run in Debug Mode

```python
demo.launch(debug=True)
```

### Auto-reload on Changes

```bash
gradio app.py --watch
```

## Resources

- [Gradio Documentation](https://gradio.app/docs/)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- Project: [LANGGRAPH_IMPLEMENTATION.md](../LANGGRAPH_IMPLEMENTATION.md)

---

**Version:** 1.0.0 (Phase 1)
**Status:** ✅ Ready to use
**Date:** 2026-01-16
