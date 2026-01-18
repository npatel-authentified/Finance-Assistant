# AI Finance Assistant - Flow Summary

## Quick Reference Guide

This is a quick reference for understanding how the AI Finance Assistant processes different types of questions.

---

## 3 Main Execution Paths

### Path 1: Fast Route (High Confidence) ⚡
**When:** Clear, unambiguous questions
**Examples:** "What is a 401k?", "Should I invest in Apple?", "How is my portfolio?"
**Flow:** `Question → Fast Router → Agent → Response`
**Time:** ~2-3 seconds
**Nodes:** 2

### Path 2: Supervised Single Agent 🎯
**When:** Ambiguous single-domain questions
**Examples:** "I want to plan for my future", "Help me invest"
**Flow:** `Question → Fast Router → Supervisor → Agent → Response`
**Time:** ~3-4 seconds
**Nodes:** 3

### Path 3: Multi-Agent Sequential 🔄
**When:** Complex questions requiring multiple domains
**Examples:** "Should I invest in Tesla given my portfolio?", "Analyze my portfolio and recommend stocks"
**Flow:** `Question → Fast Router → Supervisor → Agent1 → Router → Agent2 → Router → Agent3 → Synthesizer → Response`
**Time:** ~8-12 seconds
**Nodes:** 10-13

---

## How Each Component Works

### 1. Fast Router (Pattern Matching)

```
Input: User question
Output: Routing decision

Process:
├─ Extract keywords from question
├─ Calculate confidence scores for each agent
│  └─ Based on keyword matches
├─ Select highest scoring agent
└─ If confidence >= 0.9: Direct route
   If confidence < 0.9: Send to supervisor

Examples:
- "What is compound interest?"
  → Keywords: ["compound", "interest", "what"]
  → Education agent confidence: 0.95
  → Decision: Direct to education_agent

- "Should I invest?"
  → Keywords: ["invest"]
  → Market: 0.3, Goal: 0.3, Education: 0.2
  → All low confidence
  → Decision: Send to supervisor
```

### 2. Supervisor (LLM Analysis)

```
Input: User question + context hints from fast router
Output: Execution plan

Process:
├─ LLM analyzes the question
├─ Determines which agent(s) needed
├─ Decides execution mode:
│  ├─ "single": One agent only
│  ├─ "sequential": Multiple agents, one after another
│  └─ "parallel": (Future) Multiple agents at once
└─ Creates execution plan if multi-agent

Example:
Question: "Should I buy Tesla? I have a portfolio."

LLM Analysis:
"This requires:
 1. Portfolio analysis (check diversification)
 2. Market analysis (analyze Tesla)
 3. Recommendation (investment advice)"

Decision:
├─ primary_agent: PORTFOLIO
├─ secondary_agents: [MARKET, GOAL_PLANNING]
├─ execution_mode: "sequential"
└─ Creates execution_plan:
    {
      agents_queue: [PORTFOLIO, MARKET, GOAL_PLANNING],
      current_index: 0,
      needs_synthesis: True
    }
```

### 3. Agent Execution

```
Each agent:
├─ Receives full conversation history
├─ Uses specialized tools:
│  ├─ Education: RAG (Pinecone + GPT)
│  ├─ Portfolio: Portfolio analysis tools
│  ├─ Market: yfinance stock data
│  ├─ Goal: Financial planning tools
│  └─ News: News synthesis tools
├─ Generates response
└─ Updates state:
    ├─ Adds message to conversation
    ├─ Stores result in agent_results
    ├─ Increments execution_plan.current_index
    └─ Marks self as completed
```

### 4. Sequence Router (Traffic Director)

```
Purpose: Decide where to go next after an agent

Process:
├─ Check if execution_plan exists
│  ├─ YES: Multi-agent scenario
│  │  └─ Check execution_plan.current_index
│  │     ├─ More agents in queue?
│  │     │  └─ Route to next agent
│  │     └─ Queue complete?
│  │        └─ Route to synthesizer
│  └─ NO: Single agent scenario
│     └─ Route to END

Why needed:
- Keeps agents simple (don't need routing logic)
- Centralizes routing decisions
- Enables clean linear flow
- Avoids 35+ edges in graph
```

### 5. Synthesizer (Result Combiner)

```
Input: Multiple agent results
Output: Combined coherent response

Process:
├─ Read all results from agent_results
├─ Format each result with header:
│  "**PORTFOLIO ANALYSIS**"
│  (portfolio agent response)
│
│  "**MARKET ANALYSIS**"
│  (market agent response)
│
│  "**GOAL PLANNING ANALYSIS**"
│  (goal planning response)
├─ Add comprehensive summary
└─ Return formatted response

Future Enhancement:
- Use LLM to intelligently synthesize
- Remove redundancy
- Create coherent narrative
```

---

## State Management

### What's in the State?

```python
State = {
    # Conversation
    "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."},
        ...
    ],

    # Routing metadata
    "router_decision": {
        "route": "direct" | "supervisor",
        "agent": AgentType | None,
        "confidence": 0.0-1.0,
        "reasoning": "..."
    },

    "supervisor_decision": {
        "primary_agent": AgentType,
        "secondary_agents": [AgentType, ...],
        "execution_mode": "single" | "sequential" | "parallel",
        "reasoning": "...",
        "workflow_steps": [...]
    },

    # Multi-agent tracking
    "execution_plan": {
        "agents_queue": [AGENT1, AGENT2, AGENT3],
        "current_index": 0,  # Current position
        "needs_synthesis": True
    },

    # Results
    "agent_results": {
        "education": "...",
        "portfolio": "...",
        "market": "...",
        ...
    },

    # Completion tracking
    "agents_completed": ["education", "portfolio"],
    "current_agent": "market",
    "final_response": "..."
}
```

### State Evolution Example

**Question:** "Should I invest in Tesla?"

**Step 1 - After Fast Router:**
```python
{
    "messages": [{"role": "user", "content": "Should I invest in Tesla?"}],
    "router_decision": {
        "route": "supervisor",
        "confidence": 0.60
    }
}
```

**Step 2 - After Supervisor:**
```python
{
    "messages": [...],
    "router_decision": {...},
    "supervisor_decision": {
        "primary_agent": MARKET,
        "secondary_agents": [GOAL_PLANNING],
        "execution_mode": "sequential"
    },
    "execution_plan": {
        "agents_queue": [MARKET, GOAL_PLANNING],
        "current_index": 0
    }
}
```

**Step 3 - After Market Agent:**
```python
{
    "messages": [..., {"role": "assistant", "content": "Tesla analysis..."}],
    "execution_plan": {
        "agents_queue": [MARKET, GOAL_PLANNING],
        "current_index": 1  # ← Incremented
    },
    "agent_results": {
        "market": "Tesla is trading at..."
    },
    "agents_completed": ["market"]
}
```

**Step 4 - After Goal Planning Agent:**
```python
{
    "messages": [...],
    "execution_plan": {
        "current_index": 2  # ← Complete
    },
    "agent_results": {
        "market": "...",
        "goal_planning": "Based on analysis..."
    },
    "agents_completed": ["market", "goal_planning"]
}
```

**Step 5 - After Synthesizer:**
```python
{
    "messages": [..., {"role": "assistant", "content": "COMPREHENSIVE..."}],
    "final_response": "**MARKET ANALYSIS**\n...\n**COMPREHENSIVE**..."
}
```

---

## Routing Decisions Explained

### Decision 1: Fast Router Confidence

```
Confidence Calculation:
├─ Count keyword matches per agent
├─ Normalize by total keywords
└─ Highest score = recommended agent

Threshold:
├─ >= 0.9: High confidence → Direct route
└─ < 0.9: Low confidence → Supervisor

Tunable in: src/orchestration/router.py
```

### Decision 2: Agent Completion Routing

```
After any agent executes:

Check: Does execution_plan exist?
├─ YES (Multi-agent):
│  └─ Go to sequence_router
│     └─ sequence_router checks:
│        ├─ More agents? → Next agent
│        └─ Queue done? → Synthesizer
└─ NO (Single agent):
   └─ Go to END
```

---

## Example Traces

### Trace 1: "What is a 401k?"

```
1. fast_router_node
   Input: {"messages": [{"role": "user", "content": "What is a 401k?"}]}
   Decision: confidence=0.95, agent=EDUCATION
   Output: {"router_decision": {...}}

2. education_agent_node
   Input: Previous state + router_decision
   Action: RAG query → "401k retirement plan..."
   Output: {"messages": [..., AI response], "final_response": "..."}

3. END
```

### Trace 2: "Should I invest in Tesla given my portfolio?"

```
1. fast_router_node
   Decision: confidence=0.45 → supervisor

2. supervisor_node
   LLM Analysis: Needs portfolio + market + recommendation
   Decision: execution_mode=sequential, 3 agents
   Output: execution_plan created

3. portfolio_agent_node
   Action: Analyze portfolio
   Output: agent_results["portfolio"] = "...", current_index: 0→1

4. sequence_router_node
   Action: Pass through (no state change)

5. route_sequence()
   Decision: current_index=1 < 3 → market_agent

6. market_agent_node
   Action: Analyze Tesla
   Output: agent_results["market"] = "...", current_index: 1→2

7. sequence_router_node
   Action: Pass through

8. route_sequence()
   Decision: current_index=2 < 3 → goal_planning_agent

9. goal_planning_agent_node
   Action: Make recommendation
   Output: agent_results["goal_planning"] = "...", current_index: 2→3

10. sequence_router_node
    Action: Pass through

11. route_sequence()
    Decision: current_index=3 == 3 → synthesizer

12. synthesizer_node
    Action: Combine all 3 results
    Output: final_response = "COMPREHENSIVE..."

13. END
```

---

## Performance Characteristics

| Scenario | Nodes | LLM Calls | RAG Queries | Time |
|----------|-------|-----------|-------------|------|
| High confidence → Education | 2 | 1 | 1 | 2-3s |
| High confidence → Other agent | 2 | 1 | 0 | 1-2s |
| Low confidence → Single agent | 3 | 2 | 0-1 | 3-4s |
| Multi-agent (2 agents) | 7 | 3 | 0-2 | 6-8s |
| Multi-agent (3 agents) | 10 | 4 | 0-3 | 8-12s |

**Notes:**
- Education agent uses RAG (slower due to Pinecone query)
- Each agent call = 1 LLM call
- Supervisor = 1 LLM call
- Sequence router = 0 LLM calls (just routing logic)

---

## Memory & Conversation Context

### How Memory Works

```
1. User asks: "I have a portfolio"
   ├─ State saved with thread_id="abc123"
   └─ Checkpointer stores: [Q1, A1]

2. User asks: "How is it performing?"
   ├─ LangGraph loads previous state from thread_id
   ├─ Agent sees full context: [Q1, A1, Q2]
   ├─ Agent understands "it" refers to "portfolio"
   └─ Checkpointer saves: [Q1, A1, Q2, A2]

3. User clicks "Clear Chat"
   ├─ New thread_id generated
   └─ Fresh conversation starts
```

### Thread Isolation

```
Thread 1 (user_alice):
├─ Q: "My name is Alice"
├─ A: "Nice to meet you, Alice!"
├─ Q: "What's my name?"
└─ A: "Your name is Alice!" ✅

Thread 2 (user_bob):
├─ Q: "What's my name?"
└─ A: "I don't have that information." ✅
```

---

## Edge Cases Handled

### 1. Empty Message
```
Input: {"messages": []}
Handling: Default to education agent
```

### 2. Agent Error
```
Agent throws exception
├─ Catch error
├─ Clear execution_plan (stop multi-agent)
├─ Return error message
└─ Go to END (graceful failure)
```

### 3. Supervisor Can't Decide
```
LLM returns unclear decision
├─ Default to education agent
└─ Log warning
```

### 4. Very Long Conversation
```
100+ messages in thread
├─ Currently: All stored
└─ Future: Trim to last 20 messages
```

### 5. Mid-Sequence Failure
```
Agent 1 ✅ → Agent 2 ❌ → Agent 3 ⏸️
├─ Agent 2 error clears execution_plan
├─ Returns partial results from Agent 1
└─ Doesn't execute Agent 3
```

---

## Key Takeaways

1. **Two routing layers:** Fast router (fast, pattern-based) → Supervisor (slow, LLM-based)

2. **Sequence router is crucial:** Prevents graph complexity explosion (35+ edges → 15 edges)

3. **State drives execution:** execution_plan controls multi-agent flow

4. **Conversation memory:** Thread-based persistence via LangGraph checkpointing

5. **Graceful degradation:** Errors don't crash, default to education agent

6. **Three execution paths:** Fast single (2s) | Supervised single (4s) | Multi-agent (8-12s)

---

## Visualizations

For interactive diagrams, see:
- **APP_FLOW_GUIDE.md** - Detailed step-by-step scenarios
- **FLOW_DIAGRAMS.md** - Mermaid diagrams (paste to https://mermaid.live/)
- **financial_assistant_graph.png** - Actual graph structure

To generate the actual graph:
```bash
python -c "
from src.orchestration import create_app_with_memory
app = create_app_with_memory()
app.get_graph().draw_mermaid_png()
"
```

---

**Created:** 2026-01-17
**Purpose:** Quick reference for understanding app flow
**See Also:** APP_FLOW_GUIDE.md, FLOW_DIAGRAMS.md
