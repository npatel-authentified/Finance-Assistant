# Web UI Troubleshooting Guide

Common issues and solutions when running the AI Finance Assistant Web UI.

## Import Errors

### ✅ FIXED: ModuleNotFoundError: No module named 'src'

**Problem:**
```python
ModuleNotFoundError: No module named 'src'
```

**Solution:**
This has been fixed! The app now automatically adds the project root to Python path.

**How it works:**
```python
# In web_app/app.py
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

**Now you can run from anywhere:**
```bash
python web_app/app.py              # ✅ Works
python run_webapp.py                # ✅ Works
cd web_app && python app.py         # ✅ Works
```

### Alternative Solutions (If Still Having Issues)

**Option 1: Run as module**
```bash
# From project root
python -m web_app.app
```

**Option 2: Set PYTHONPATH**
```bash
export PYTHONPATH=/path/to/ai_finance_assistant:$PYTHONPATH
python web_app/app.py
```

**Option 3: Install in development mode**
```bash
pip install -e .
# Then run from anywhere
```

---

## Gradio Installation

### ModuleNotFoundError: No module named 'gradio'

**Solution:**
```bash
uv pip install gradio
# or
pip install gradio
```

**Verify installation:**
```bash
python -c "import gradio; print(gradio.__version__)"
```

---

## LangGraph/Agent Errors

### No module named 'src.orchestration'

**Cause:** Project root not in Python path

**Solution:** Already fixed in app.py (see above)

### Agent execution fails

**Common causes:**

1. **Missing API Key**
```bash
export OPENAI_API_KEY="your-key-here"
```

2. **Missing Dependencies**
```bash
# For full functionality
uv pip install pinecone-client yfinance pandas numpy
```

3. **Pinecone not configured**
```bash
export PINECONE_API_KEY="your-key"
export PINECONE_INDEX_NAME="finance-docs"
```

---

## Port Issues

### Address already in use (Port 7860)

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution 1: Kill existing process**
```bash
# macOS/Linux
lsof -ti:7860 | xargs kill -9

# Or find and kill manually
lsof -i :7860
kill -9 <PID>
```

**Solution 2: Use different port**

Edit `web_app/app.py`:
```python
demo.launch(server_port=7861)  # Changed from 7860
```

---

## Performance Issues

### Slow responses

**Normal behavior:**
- Single agent: 3-10 seconds
- Multi-agent: 10-30 seconds

**Why:**
- LLM API calls (OpenAI)
- Vector search (Pinecone/RAG)
- Market data fetching (yfinance)

**Tips:**
- Use specific questions (faster routing)
- Clear chat periodically (less context = faster)
- Education agent is fastest (cached RAG)

### UI freezes

**Cause:** Synchronous execution blocking UI

**Solution:** Already implemented! Uses async generators:
```python
def chat_with_assistant(...) -> Generator:
    for chunk in app.stream(...):
        yield history, status  # Non-blocking
```

---

## Browser Issues

### Browser doesn't open automatically

**Solution:**
1. Manually open: http://localhost:7860
2. Or enable auto-open in `app.py`:
```python
demo.launch(inbrowser=True)
```

### Can't access from other devices

**Current (Local only):**
```python
demo.launch(server_name="0.0.0.0")
```

**For public access:**
```python
demo.launch(share=True)  # Creates temporary public URL
```

---

## Development Issues

### Changes not reflected

**Solution:** Restart the app
```bash
# Stop with Ctrl+C
# Restart
python web_app/app.py
```

**Auto-reload (development):**
```bash
gradio web_app/app.py --watch
```

### Debug mode

**Enable verbose errors:**
```python
demo.launch(debug=True, show_error=True)
```

---

## Testing

### Test UI without dependencies

```bash
python web_app/test_ui.py
```

This runs a minimal mock version that doesn't require:
- LangGraph
- OpenAI API
- Pinecone
- Any agents

**Good for:**
- Verifying Gradio works
- Testing UI layout
- Quick visual check

---

## Common Error Messages

### "No response generated"

**Cause:** Agent execution failed silently

**Check:**
1. Status box for error details
2. Terminal output for stack trace
3. API keys are set

### "Thread ID error"

**Rare:** State persistence issue

**Solution:** Click "Clear Chat" to reset

### "Streaming error"

**Cause:** LangGraph streaming failed

**Check:**
1. LangGraph version: `pip list | grep langgraph`
2. Update if needed: `uv pip install -U langgraph`

---

## File Locations

If you see "File not found" errors:

**Correct structure:**
```
ai_finance_assistant/
├── src/
│   └── orchestration/
├── web_app/
│   ├── app.py          ← Main app
│   ├── test_ui.py      ← Test app
│   └── TROUBLESHOOTING.md  ← This file
└── run_webapp.py       ← Launcher
```

**Run from project root:**
```bash
cd /path/to/ai_finance_assistant
python web_app/app.py
```

---

## Still Having Issues?

### Check Python version
```bash
python --version
# Should be 3.9+
```

### Check dependencies
```bash
pip list | grep -E "gradio|langgraph|langchain"
```

### Verify project structure
```bash
ls -la src/orchestration/
# Should show: __init__.py, graph.py, nodes.py, etc.
```

### Run simple test
```bash
python -c "from src.orchestration import create_app_with_memory; print('OK')"
```

### Get detailed error
```bash
python web_app/app.py 2>&1 | tee error.log
```

---

## Quick Diagnostic

Run this diagnostic script:

```python
# diagnostic.py
import sys
print(f"Python: {sys.version}")
print(f"Path: {sys.path}")

try:
    import gradio
    print(f"✅ Gradio: {gradio.__version__}")
except ImportError:
    print("❌ Gradio not installed")

try:
    from src.orchestration import create_app_with_memory
    print("✅ Can import src.orchestration")
except ImportError as e:
    print(f"❌ Cannot import src.orchestration: {e}")

try:
    import os
    print(f"OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
except:
    pass
```

Run it:
```bash
python diagnostic.py
```

---

**Still stuck?** Check the main project documentation:
- README.md
- WEB_UI_GUIDE.md
- LANGGRAPH_IMPLEMENTATION.md
