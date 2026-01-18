# AI Finance Assistant - Quick Reference Card

## 🎯 Three Execution Paths

| Path | When | Example | Nodes | Time |
|------|------|---------|-------|------|
| **⚡ Fast Route** | Clear question | "What is a 401k?" | 2 | 2-3s |
| **🎯 Supervised** | Ambiguous question | "Help me plan" | 3 | 3-4s |
| **🔄 Multi-Agent** | Complex question | "Invest in Tesla?" | 10+ | 8-12s |

---

## 📊 Component Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Fast Router │ => │ Supervisor  │ => │   Agents    │ => │Synthesizer  │
│  (Pattern)  │    │    (LLM)    │    │  (Execute)  │    │  (Combine)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
  Confidence          Creates            Run tools         Format final
   >= 0.9?         execution_plan       & generate         response
```

---

## 🧠 5 Specialized Agents

| Agent | Purpose | Tools | Example |
|-------|---------|-------|---------|
| 📚 **Education** | Financial concepts | RAG (Pinecone) | "What is a Roth IRA?" |
| 🎯 **Goal Planning** | Set financial goals | Planning tools | "Save for retirement" |
| 💼 **Portfolio** | Analyze holdings | Analysis tools | "How's my portfolio?" |
| 📈 **Market** | Stock analysis | yfinance | "Should I buy Tesla?" |
| 📰 **News** | Investment research | News synthesis | "AI stock news" |

---

## 🔀 Routing Logic

### Fast Router (Keyword-Based)
```python
Confidence >= 0.9 → Direct to agent
Confidence <  0.9 → Send to supervisor
```

### Supervisor (LLM-Based)
```python
Single domain   → execution_mode="single"  → 1 agent
Multiple domains → execution_mode="sequential" → N agents → synthesizer
```

### Sequence Router (Traffic Director)
```python
execution_plan exists?
├─ YES → More agents in queue?
│        ├─ YES → Next agent
│        └─ NO  → Synthesizer
└─ NO  → END
```

---

## 📦 State Structure

```python
{
    "messages": [...],              # Conversation history
    "router_decision": {...},       # Fast router output
    "supervisor_decision": {...},   # Supervisor output
    "execution_plan": {             # Multi-agent tracking
        "agents_queue": [A1, A2],
        "current_index": 0
    },
    "agent_results": {              # Accumulated results
        "education": "...",
        "portfolio": "..."
    },
    "final_response": "..."         # Final answer
}
```

---

## 🎬 Example Scenarios

### Scenario 1: Simple Question
```
"What is compound interest?"
  ↓
Fast Router (confidence: 0.95)
  ↓
Education Agent (RAG query)
  ↓
Response: "Compound interest is..."
```

### Scenario 2: Ambiguous Question
```
"I want to invest"
  ↓
Fast Router (confidence: 0.40)
  ↓
Supervisor (LLM decides: goal_planning)
  ↓
Goal Planning Agent
  ↓
Response: "Let's create an investment plan..."
```

### Scenario 3: Complex Multi-Agent
```
"Should I invest in Tesla given my portfolio?"
  ↓
Fast Router (confidence: 0.45)
  ↓
Supervisor (decides: portfolio → market → goal)
  ↓
Portfolio Agent → "60% tech stocks..."
  ↓
Sequence Router
  ↓
Market Agent → "Tesla at $250..."
  ↓
Sequence Router
  ↓
Goal Planning Agent → "Based on analysis..."
  ↓
Sequence Router
  ↓
Synthesizer → Combines all 3
  ↓
Response: "**PORTFOLIO**\n...\n**MARKET**\n...\n**COMPREHENSIVE**"
```

---

## 🛡️ Edge Cases

| Case | Handling |
|------|----------|
| Empty message | Default to education agent |
| Agent error | Return error message, stop sequence |
| Supervisor unclear | Default to education agent |
| Very long conversation | (Future) Trim to last 20 messages |
| Mid-sequence failure | Return partial results |

---

## 💾 Memory System

```
Thread-based persistence:
├─ Each conversation has unique thread_id
├─ LangGraph checkpointer saves state after each node
├─ On next message, loads previous state
└─ "Clear Chat" creates new thread_id

Example:
Q1: "I have a portfolio" (thread_id: abc)
  → Saved: [Q1, A1]

Q2: "How is it performing?" (thread_id: abc)
  → Loaded: [Q1, A1]
  → Agent sees context: "it" = portfolio ✅
  → Saved: [Q1, A1, Q2, A2]
```

---

## 📈 Performance

| Component | LLM Calls | Time |
|-----------|-----------|------|
| Fast Router | 0 | <100ms |
| Supervisor | 1 | ~1s |
| Education Agent | 1 + RAG | ~2s |
| Other Agents | 1 | ~1s |
| Synthesizer | 0 | <100ms |
| Sequence Router | 0 | <10ms |

**Total Examples:**
- Fast route → education: 1 LLM + RAG = ~2s
- Supervised → single: 2 LLM = ~2s
- Multi-agent (3): 4 LLM = ~6-8s

---

## 🔑 Key Insights

1. **Two-tier routing**: Fast (pattern) → Supervisor (LLM)
2. **Sequence router critical**: Prevents graph explosion (35 edges → 15)
3. **State-driven execution**: execution_plan controls flow
4. **Conversation memory**: Thread-based via checkpointing
5. **Graceful degradation**: Errors don't crash system

---

## 🎨 Visual Flow

```
              START
                │
         ┌──────▼──────┐
         │Fast Router  │
         └──┬────────┬──┘
            │        │
       High │   Low  │ Confidence
            │        │
            ▼        ▼
       ┌────────┐  ┌──────────┐
       │ Agent  │  │Supervisor│
       └───┬────┘  └─┬────────┘
           │         │
           │    ┌────┴─────┐
           │    │          │
           │ Single    Sequential
           │    │          │
           │    ▼          ▼
           │ ┌────┐    ┌──────┐
           │ │Agt │    │Agent1│
           │ └──┬─┘    └──┬───┘
           │    │         │
           │    │         ▼
           │    │      ┌─────────┐
           │    │      │Seq Route│
           │    │      └──┬──────┘
           │    │         │
           │    │         ▼
           │    │      ┌──────┐
           │    │      │Agent2│
           │    │      └──┬───┘
           │    │         │
           │    │         ▼
           │    │      ┌──────────┐
           │    │      │Synthesize│
           │    │      └──┬───────┘
           │    │         │
           └────┴─────────┘
                │
                ▼
               END
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Main project documentation |
| **APP_FLOW_GUIDE.md** | Detailed scenarios & step-by-step |
| **FLOW_DIAGRAMS.md** | Interactive Mermaid diagrams |
| **FLOW_SUMMARY.md** | Comprehensive flow reference |
| **QUICK_REFERENCE.md** | This file - one-page summary |
| **ANNOTATED_EXPLAINED.md** | State reducer explanation |
| **LANGGRAPH_IMPLEMENTATION.md** | Architecture details |
| **WEB_UI_GUIDE.md** | Web interface usage |

---

## 🚀 Quick Commands

```bash
# Run web UI
python web_app/app.py

# Run CLI
python main_langgraph.py "Your question here"

# Test UI (no dependencies)
python web_app/test_ui.py

# Run tests
pytest

# Generate graph visualization
python -c "from src.orchestration import create_app_with_memory; \
  app = create_app_with_memory(); \
  print(app.get_graph().draw_mermaid())"
```

---

## 🔗 Interactive Diagrams

**View diagrams online:**
1. Open `FLOW_DIAGRAMS.md`
2. Copy any Mermaid diagram
3. Paste to https://mermaid.live/
4. View interactive visualization

---

**Created:** 2026-01-17
**Last Updated:** 2026-01-17
**Version:** 1.0
