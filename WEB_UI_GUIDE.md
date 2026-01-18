# AI Finance Assistant - Web UI Guide

Complete guide for the Gradio-based web interface.

## 📋 Overview

The web UI provides a clean, modern chat interface for interacting with the AI Finance Assistant. It uses **Gradio** for the frontend and **LangGraph** for the backend multi-agent orchestration.

### Key Features (Phase 1)

✅ **Real-time Streaming** - See agent execution progress live
✅ **Multi-Agent Routing** - Automatic intelligent routing
✅ **Conversation Persistence** - Thread-based memory
✅ **Clean Interface** - Professional, modern design
✅ **Example Questions** - Quick start prompts
✅ **Status Updates** - Real-time workflow visibility

---

## 🚀 Quick Start

### 1. Install Gradio

```bash
uv pip install gradio
```

### 2. Launch the App

**Option A: Using run script (Easiest)**
```bash
python run_webapp.py
```

**Option B: Direct launch**
```bash
python web_app/app.py
```

**Option C: With uv**
```bash
uv run python web_app/app.py
```

### 3. Open Browser

The app will automatically open at: **http://localhost:7860**

---

## 💬 How to Use

### Ask Questions

Type any finance-related question:

**Portfolio Analysis:**
- "How is my portfolio performing?"
- "What stocks should I sell?"
- "Analyze my portfolio risk"

**Market Research:**
- "Should I invest in Tesla?"
- "What's happening in the tech sector?"
- "Give me market analysis for AAPL"

**Financial Education:**
- "What is compound interest?"
- "Explain diversification"
- "How do ETFs work?"

**Goal Planning:**
- "Help me plan for retirement"
- "I want to save for a house"
- "Create a financial goal for college"

### Watch Execution Progress

The **Status** box shows real-time updates:

```
🔍 Fast Router: Routing to portfolio agent (confidence: 0.95)
▶️  Executing portfolio agent...
✅ Response complete
```

**Multi-Agent Example:**
```
🔍 Fast Router → Supervisor (confidence: 0.60)
🎯 Supervisor: market + news (sequential)
▶️  Executing market agent...
➡️  Routing to next agent...
▶️  Executing news agent...
📋 Synthesizing results from multiple agents...
✅ Response complete
```

### Clear Chat

Click **"🗑️ Clear Chat"** to:
- Clear conversation history
- Start new thread
- Reset context

---

## 🎨 Interface Layout

```
┌────────────────────────────────────────────────────────────────┐
│  🤖 AI Finance Assistant                                        │
│                                                                 │
│  Ask questions about finance, investments, portfolio            │
│  analysis, and financial planning.                              │
│                                                                 │
│  Specialized agents: Education | Goal Planning | Portfolio |    │
│                     Market | News                               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  💬 Chat History                                                │
│  ─────────────────────────────────────────────────────────     │
│                                                                 │
│  You: Should I invest in Tesla?                                │
│                                                                 │
│  🤖: Based on current market analysis...                        │
│      Tesla (TSLA) current price: $245.32                       │
│      • P/E Ratio: 68.5                                         │
│      • Market Cap: $778B                                       │
│      ...                                                        │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│  Status: ✅ Response complete                                   │
├────────────────────────────────────────────────────────────────┤
│  [Ask a question...                              ] [Send 📤]   │
├────────────────────────────────────────────────────────────────┤
│  🗑️ Clear Chat         Thread ID: session_abc12345             │
├────────────────────────────────────────────────────────────────┤
│  Example Questions:                                             │
│  • How is my portfolio performing?                              │
│  • What is compound interest?                                   │
│  • Should I invest in Tesla?                                    │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Change Port

Edit `web_app/app.py`:
```python
demo.launch(
    server_port=7861,  # Change from 7860
)
```

### Create Public Link

Temporary shareable link:
```python
demo.launch(
    share=True,  # Creates temporary public URL
)
```

### Add Authentication

Basic auth protection:
```python
demo.launch(
    auth=("username", "password"),
)
```

### Custom Theme

Change appearance:
```python
with gr.Blocks(theme=gr.themes.Glass()) as demo:
    # Or: Soft, Monochrome, Default
    ...
```

---

## 🏗️ Architecture

```
User Browser
    ↓
Gradio Web UI (Port 7860)
    ↓
web_app/app.py
    ↓
src.orchestration.create_app_with_memory()
    ↓
LangGraph StateGraph
    ↓
┌─────────────────────────────────────┐
│  Fast Router                        │
│    ↓                                │
│  Supervisor                         │
│    ↓                                │
│  Agents (Education, Portfolio, etc) │
│    ↓                                │
│  Sequence Router                    │
│    ↓                                │
│  Synthesizer                        │
└─────────────────────────────────────┘
    ↓
Agent Response
    ↓
Gradio UI (Stream updates)
    ↓
User Browser
```

### Streaming Flow

1. **User sends message** → Gradio receives input
2. **Create LangGraph stream** → Start workflow execution
3. **Stream updates** → Each node execution sends status
4. **Format updates** → Convert to readable status messages
5. **Yield to UI** → Real-time display in status box
6. **Final response** → Update chat history

---

## 🧪 Testing

### Test UI Only (No Dependencies)

```bash
python web_app/test_ui.py
```

This creates a mock interface to verify Gradio works without requiring LangGraph/agents.

### Test Full App

```bash
# Make sure dependencies are installed
python web_app/app.py
```

---

## 🐛 Troubleshooting

### Port Already in Use

**Error:** `OSError: [Errno 48] Address already in use`

**Solution:**
```bash
# Kill process on port 7860
lsof -ti:7860 | xargs kill -9

# Or use different port in app.py
demo.launch(server_port=7861)
```

### Gradio Not Found

**Error:** `ModuleNotFoundError: No module named 'gradio'`

**Solution:**
```bash
uv pip install gradio
# or
pip install gradio
```

### LangGraph Import Error

**Error:** `ModuleNotFoundError: No module named 'src.orchestration'`

**Solution:**
```bash
# Make sure you're in project root
cd /path/to/ai_finance_assistant

# Run from project root
python web_app/app.py
```

### Agent Execution Errors

**Error:** Agent fails during execution

**Check:**
1. **API Keys:** `OPENAI_API_KEY` must be set
2. **Dependencies:** Install `pinecone-client`, `yfinance`, etc.
3. **Status Box:** Shows specific error message

**Solution:**
```bash
# Set API key
export OPENAI_API_KEY="your-key-here"

# Install dependencies
uv pip install pinecone-client yfinance pandas numpy
```

### Slow Response

**Issue:** Takes long time to respond

**Reasons:**
- LLM API calls (supervisor routing)
- RAG vector search (education agent)
- Market data fetching (market/news agents)

**Normal behavior:** Sequential multi-agent can take 10-30 seconds

### Browser Doesn't Open

**Issue:** App starts but browser doesn't open

**Solution:**
1. Manually open: http://localhost:7860
2. Or enable auto-open:
   ```python
   demo.launch(inbrowser=True)
   ```

---

## 📊 Understanding Status Messages

### Router Messages

```
🔍 Fast Router: Routing to portfolio agent (confidence: 0.95)
```
- **0.9-1.0:** Very confident, direct routing
- **0.7-0.9:** Confident
- **Below 0.7:** Low confidence, uses supervisor

```
🔍 Fast Router: Using supervisor (confidence: 0.45)
```
- Question is ambiguous or multi-faceted
- Supervisor will analyze and route

### Supervisor Messages

```
🎯 Supervisor: portfolio agent
```
- Single agent selected

```
🎯 Supervisor: market + ['news'] (sequential)
```
- Multiple agents needed
- Will execute in sequence

### Agent Execution

```
▶️  Executing portfolio agent...
```
- Agent is currently running
- Processing your question

```
➡️  Routing to next agent...
```
- Sequence router determining next step
- In multi-agent workflow

```
📋 Synthesizing results from multiple agents...
```
- Combining outputs from multiple agents
- Creating coherent response

### Completion

```
✅ Response complete
```
- Workflow finished
- Response ready

---

## 🎯 Phase 2 Preview (Coming Soon)

Phase 2 will add:

### Enhanced UI
```
┌─────────────┬──────────────────────────────────────┐
│  Sidebar    │  Chat Interface                      │
│  ─────────  │  ────────────────────────────────    │
│  📊 Stats   │  Conversation here...                │
│  🔀 Graph   │                                      │
│  ⚙️ Settings│                                      │
└─────────────┴──────────────────────────────────────┘
```

### New Features
- 📊 **Agent Usage Stats** - See which agents used most
- 🔀 **Workflow Visualization** - Interactive graph display
- 💾 **Export Chat** - Save conversations
- 🎨 **Themes** - Light/dark mode
- 📈 **Analytics Dashboard** - Usage insights
- ⚙️ **Settings Panel** - Customize behavior

---

## 📁 File Structure

```
web_app/
├── __init__.py          # Package initialization
├── app.py               # Main Gradio application
├── test_ui.py           # UI test (no dependencies)
└── README.md            # Documentation

run_webapp.py            # Launcher script (project root)
WEB_UI_GUIDE.md         # This guide (project root)
```

---

## 🔗 Resources

- **Gradio Docs:** https://gradio.app/docs/
- **LangGraph Docs:** https://python.langchain.com/docs/langgraph
- **Project Docs:** [LANGGRAPH_IMPLEMENTATION.md](LANGGRAPH_IMPLEMENTATION.md)
- **Graph Simplification:** [GRAPH_SIMPLIFICATION.md](GRAPH_SIMPLIFICATION.md)

---

## 💡 Tips

### Best Questions

**Specific is better:**
- ❌ "Tell me about investing"
- ✅ "What's the difference between ETFs and mutual funds?"

**Context helps:**
- ❌ "Should I invest?"
- ✅ "Should I invest in Tesla given the recent earnings report?"

**Use examples:**
- "Analyze my portfolio: AAPL 10 shares, GOOGL 5 shares"
- "Create a retirement goal: save $1M by age 65"

### Performance Tips

- Clear chat periodically (long threads = more tokens)
- Single-agent questions are faster than multi-agent
- Education agent (RAG) is fastest
- Market/news agents may be slower (external APIs)

---

**Version:** 1.0.0 (Phase 1)
**Status:** ✅ Production Ready
**Date:** 2026-01-16

Enjoy your AI Finance Assistant! 🚀
