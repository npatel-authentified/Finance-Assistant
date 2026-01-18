# AI Finance Assistant - Complete Flow Guide

## Table of Contents
1. [Overview](#overview)
2. [Scenario 1: High Confidence Single Agent](#scenario-1-high-confidence-single-agent)
3. [Scenario 2: Low Confidence Single Agent](#scenario-2-low-confidence-single-agent)
4. [Scenario 3: Multi-Agent Sequential](#scenario-3-multi-agent-sequential)
5. [Edge Cases](#edge-cases)
6. [State Flow](#state-flow)
7. [Decision Points](#decision-points)

---

## Overview

### Complete Graph Structure

```
                           START
                             │
                             ▼
                    ┌────────────────┐
                    │  Fast Router   │ (Keyword/pattern matching)
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
         Confidence                    Confidence
           ≥ 0.9                         < 0.9
              │                             │
              ▼                             ▼
        ┌──────────┐                 ┌─────────────┐
        │  Agent   │                 │ Supervisor  │ (LLM decision)
        │ (Direct) │                 └──────┬──────┘
        └────┬─────┘                        │
             │                          Creates
             │                       execution_plan?
             │                              │
             │                    ┌─────────┴─────────┐
             │                    │                   │
             │                 Single              Multi-agent
             │                    │                   │
             │                    ▼                   ▼
             │              ┌──────────┐        ┌──────────┐
             │              │  Agent   │        │  Agent1  │
             │              └────┬─────┘        └────┬─────┘
             │                   │                   │
             │                   │              execution_plan
             │                   │              exists? YES
             │                   │                   │
             │                   │                   ▼
             │                   │           ┌────────────────┐
             │                   │           │sequence_router │
             │                   │           └───────┬────────┘
             │                   │                   │
             │                   │              Check queue
             │                   │                   │
             │                   │          ┌────────┴────────┐
             │                   │          │                 │
             │                   │    More agents?         Queue
             │                   │          │              complete?
             │                   │          ▼                 │
             │                   │    ┌──────────┐           │
             │                   │    │  Agent2  │           │
             │                   │    └────┬─────┘           │
             │                   │         │                 │
             │                   │    (Loop back             │
             │                   │    to sequence_           │
             │                   │     router)               │
             │                   │                           │
             │                   │                           ▼
             │                   │                  ┌────────────────┐
             │                   │                  │  Synthesizer   │
             │                   │                  └───────┬────────┘
             │                   │                          │
             └───────────────────┴──────────────────────────┘
                                 │
                                 ▼
                               END
```

---

## Scenario 1: High Confidence Single Agent

### Question: "What is a 401k?"

**Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Input                                                   │
│    Question: "What is a 401k?"                                  │
│    State: {messages: [{"role": "user", "content": "What..."}]}  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Fast Router                                                  │
│    Keywords detected: ["401k", "retirement account"]            │
│    Pattern: Financial education question                        │
│    Decision:                                                    │
│      - route: "direct"                                          │
│      - agent: AgentType.EDUCATION                               │
│      - confidence: 0.95                                         │
│      - reasoning: "Clear financial education question"          │
│                                                                 │
│    State updated:                                               │
│      router_decision: RouterDecision(...)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │ route_after_fast_router│
                │ Returns: "education_   │
                │          agent"        │
                └────────┬───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Education Agent                                              │
│    - Reads messages from state                                  │
│    - Queries RAG (Pinecone) for "401k" information             │
│    - Generates response using GPT-4o-mini                       │
│                                                                 │
│    Response: "A 401(k) is a retirement savings plan..."         │
│                                                                 │
│    State updated:                                               │
│      messages: [..., {"role": "assistant", "content": "..."}]   │
│      agent_results: {"education": "A 401(k) is..."}            │
│      agents_completed: ["education"]                            │
│      current_agent: "education"                                 │
│      final_response: "A 401(k) is..."                          │
│      execution_plan: None (single agent)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                   ┌─────────────────┐
                   │ route_after_    │
                   │ agent           │
                   │                 │
                   │ execution_plan? │
                   │ NO              │
                   │ Returns: "end"  │
                   └────────┬────────┘
                            │
                            ▼
                          ┌───┐
                          │END│
                          └───┘
```

### Step-by-Step Execution

| Step | Node | Input State | Output State | Routing Decision |
|------|------|-------------|--------------|------------------|
| 1 | fast_router | `messages: ["What is a 401k?"]` | `router_decision: {route: "direct", agent: EDUCATION, confidence: 0.95}` | → education_agent |
| 2 | education_agent | `router_decision` | `messages: [..., AI response], final_response: "..."` | → END |

**Total Steps:** 2 nodes
**Total Time:** ~2-3 seconds (RAG retrieval + LLM)

---

## Scenario 2: Low Confidence Single Agent

### Question: "I want to plan something for my future"

**Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Input                                                   │
│    Question: "I want to plan something for my future"           │
│    State: {messages: [{"role": "user", "content": "I want..."}]}│
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Fast Router                                                  │
│    Keywords detected: ["plan", "future"]                        │
│    Pattern: Ambiguous - could be goal planning, retirement,     │
│             education, etc.                                     │
│    Decision:                                                    │
│      - route: "supervisor"                                      │
│      - agent: None                                              │
│      - confidence: 0.65 (< 0.9 threshold)                       │
│      - reasoning: "Ambiguous question, needs LLM analysis"      │
│      - context_hints: {"goal_keywords": 2, "education": 1}      │
│                                                                 │
│    State updated:                                               │
│      router_decision: RouterDecision(...)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │ route_after_fast_router│
                │ Returns: "supervisor"  │
                └────────┬───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Supervisor                                                   │
│    - Reads user question and context hints                      │
│    - LLM analyzes: "User wants to plan for future"             │
│    - LLM Decision:                                              │
│      primary_agent: AgentType.GOAL_PLANNING                     │
│      secondary_agents: []                                       │
│      execution_mode: "single"                                   │
│      reasoning: "Clear goal planning request"                   │
│                                                                 │
│    State updated:                                               │
│      supervisor_decision: SupervisorDecision(...)               │
│      execution_plan: None (single mode)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
               ┌─────────────────────────┐
               │ route_after_supervisor  │
               │ Returns: "goal_planning_│
               │          agent"         │
               └────────┬────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Goal Planning Agent                                          │
│    - Reads messages from state                                  │
│    - Uses goal planning tools                                   │
│    - Generates personalized financial plan                      │
│                                                                 │
│    Response: "Let's create a financial plan for your future..." │
│                                                                 │
│    State updated:                                               │
│      messages: [..., AI response]                               │
│      agent_results: {"goal_planning": "..."}                    │
│      final_response: "..."                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                   ┌─────────────────┐
                   │ route_after_    │
                   │ agent           │
                   │ Returns: "end"  │
                   └────────┬────────┘
                            │
                            ▼
                          ┌───┐
                          │END│
                          └───┘
```

### Step-by-Step Execution

| Step | Node | Key Decision | Output |
|------|------|--------------|--------|
| 1 | fast_router | Confidence: 0.65 < 0.9 | → supervisor |
| 2 | supervisor | LLM decides: goal_planning, single mode | → goal_planning_agent |
| 3 | goal_planning_agent | Execute agent | → END |

**Total Steps:** 3 nodes
**Total Time:** ~3-4 seconds (extra LLM call for supervisor)

---

## Scenario 3: Multi-Agent Sequential

### Question: "Should I invest in Tesla? Consider my current portfolio."

**Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Input                                                   │
│    Question: "Should I invest in Tesla? Consider my portfolio." │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Fast Router                                                  │
│    Keywords: ["invest", "Tesla", "portfolio"]                   │
│    Pattern: Multiple domains (market + portfolio)               │
│    Confidence: 0.45 (very ambiguous)                            │
│    Decision: route → "supervisor"                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Supervisor (LLM Analysis)                                    │
│    LLM reasoning:                                               │
│    "Need to:                                                    │
│     1. Analyze current portfolio (PORTFOLIO agent)              │
│     2. Analyze Tesla stock (MARKET agent)                       │
│     3. Make recommendation (GOAL_PLANNING agent)"               │
│                                                                 │
│    Decision:                                                    │
│      primary_agent: PORTFOLIO                                   │
│      secondary_agents: [MARKET, GOAL_PLANNING]                  │
│      execution_mode: "sequential"                               │
│      workflow_steps: [                                          │
│        "1. Check portfolio diversification",                    │
│        "2. Analyze Tesla stock fundamentals",                   │
│        "3. Make investment recommendation"                      │
│      ]                                                          │
│                                                                 │
│    State updated:                                               │
│      supervisor_decision: SupervisorDecision(...)               │
│      execution_plan: {                                          │
│        agents_queue: [PORTFOLIO, MARKET, GOAL_PLANNING],        │
│        current_index: 0,                                        │
│        needs_synthesis: True                                    │
│      }                                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │ route_after_supervisor │
                │ Returns: "portfolio_   │
                │          agent"        │
                └────────┬───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Portfolio Agent (Agent 1 of 3)                               │
│    - Analyzes user's portfolio                                  │
│    - Checks diversification, risk exposure                      │
│                                                                 │
│    Response: "Your portfolio is 60% tech stocks..."             │
│                                                                 │
│    State updated:                                               │
│      messages: [..., AI response]                               │
│      agent_results: {"portfolio": "Your portfolio..."}          │
│      agents_completed: ["portfolio"]                            │
│      execution_plan: {                                          │
│        agents_queue: [PORTFOLIO, MARKET, GOAL_PLANNING],        │
│        current_index: 1,  ← INCREMENTED                         │
│        needs_synthesis: True                                    │
│      }                                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                   ┌─────────────────┐
                   │ route_after_    │
                   │ agent           │
                   │                 │
                   │ execution_plan? │
                   │ YES             │
                   │ Returns:        │
                   │ "sequence_      │
                   │  router"        │
                   └────────┬────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Sequence Router (Routing Checkpoint)                         │
│    - Just passes state through                                  │
│    - No modifications                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                   ┌─────────────────┐
                   │ route_sequence  │
                   │                 │
                   │ Check queue:    │
                   │ current_index=1 │
                   │ queue_length=3  │
                   │                 │
                   │ 1 < 3? YES      │
                   │ Returns:        │
                   │ "market_agent"  │
                   └────────┬────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Market Agent (Agent 2 of 3)                                  │
│    - Fetches Tesla stock data (yfinance)                        │
│    - Analyzes fundamentals, trends                              │
│                                                                 │
│    Response: "Tesla (TSLA) is trading at $250..."               │
│                                                                 │
│    State updated:                                               │
│      agent_results: {                                           │
│        "portfolio": "...",                                      │
│        "market": "Tesla is trading..."                          │
│      }                                                          │
│      execution_plan.current_index: 2 ← INCREMENTED              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
            ┌────────────────────────────┐
            │ route_after_agent          │
            │ Returns: "sequence_router" │
            └────────┬───────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Sequence Router (2nd time)                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │ route_sequence      │
                   │ current_index=2     │
                   │ queue_length=3      │
                   │ 2 < 3? YES          │
                   │ Returns:            │
                   │ "goal_planning_     │
                   │  agent"             │
                   └────────┬────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. Goal Planning Agent (Agent 3 of 3)                           │
│    - Reads portfolio analysis from agent_results                │
│    - Reads Tesla analysis from agent_results                    │
│    - Makes investment recommendation                            │
│                                                                 │
│    Response: "Based on your portfolio and Tesla analysis..."    │
│                                                                 │
│    State updated:                                               │
│      agent_results: {                                           │
│        "portfolio": "...",                                      │
│        "market": "...",                                         │
│        "goal_planning": "Based on..."                           │
│      }                                                          │
│      execution_plan.current_index: 3 ← INCREMENTED              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
            ┌────────────────────────────┐
            │ route_after_agent          │
            │ Returns: "sequence_router" │
            └────────┬───────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. Sequence Router (3rd time)                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │ route_sequence      │
                   │ current_index=3     │
                   │ queue_length=3      │
                   │ 3 < 3? NO           │
                   │ Queue complete!     │
                   │ Returns:            │
                   │ "synthesize"        │
                   └────────┬────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 10. Synthesizer                                                 │
│     - Reads all agent results                                   │
│     - Combines into coherent response                           │
│                                                                 │
│     Output:                                                     │
│     "**PORTFOLIO ANALYSIS**                                     │
│      Your portfolio is 60% tech stocks...                       │
│                                                                 │
│      **MARKET ANALYSIS**                                        │
│      Tesla is trading at $250...                                │
│                                                                 │
│      **GOAL PLANNING ANALYSIS**                                 │
│      Based on your portfolio...                                 │
│                                                                 │
│      **COMPREHENSIVE ANALYSIS**                                 │
│      Based on analysis from 3 agents..."                        │
│                                                                 │
│     State updated:                                              │
│       final_response: "..."                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                          ┌───┐
                          │END│
                          └───┘
```

### Step-by-Step Execution

| Step | Node | Action | State Changes |
|------|------|--------|---------------|
| 1 | fast_router | Low confidence (0.45) | → supervisor |
| 2 | supervisor | Create execution plan | execution_plan: [PORTFOLIO, MARKET, GOAL] |
| 3 | portfolio_agent | Execute agent 1 | current_index: 0→1 |
| 4 | sequence_router | Pass through | - |
| 5 | route_sequence | Check queue (1<3) | → market_agent |
| 6 | market_agent | Execute agent 2 | current_index: 1→2 |
| 7 | sequence_router | Pass through | - |
| 8 | route_sequence | Check queue (2<3) | → goal_planning_agent |
| 9 | goal_planning_agent | Execute agent 3 | current_index: 2→3 |
| 10 | sequence_router | Pass through | - |
| 11 | route_sequence | Check queue (3=3) | → synthesizer |
| 12 | synthesizer | Combine results | final_response |
| 13 | END | - | - |

**Total Steps:** 13 node executions (3 agents + routing overhead)
**Total Time:** ~8-12 seconds (3 agent calls + synthesis)

---

## Edge Cases

### Edge Case 1: Empty Message

**Input:**
```python
{"messages": []}
```

**Flow:**
```
START → fast_router → (no messages found) → default to education_agent → END
```

**Code Handling:**
```python
# In fast_router_node
messages = state.get("messages", [])
if not messages:
    # Default to education agent
    return {
        "router_decision": RouterDecision(
            route="direct",
            agent=AgentType.EDUCATION,
            confidence=0.5,
            reasoning="No message provided, defaulting to education"
        )
    }
```

---

### Edge Case 2: Agent Throws Error

**Scenario:** Portfolio agent fails (user has no portfolio)

**Flow:**
```
START → fast_router → portfolio_agent → (ERROR) →
  Return error message as response → END
```

**Code Handling:**
```python
# In _execute_agent_node
try:
    response = agent_function(question)
except Exception as e:
    response = f"I encountered an error: {str(e)}. Please try rephrasing your question."
```

**Result:** Graceful error message to user

---

### Edge Case 3: Supervisor Can't Decide

**Scenario:** Completely random/nonsensical input

**Input:** "asdfkjhasdf random text 12345"

**Flow:**
```
START → fast_router (confidence: 0.1) → supervisor →
  (LLM analysis: unclear) → defaults to education_agent → END
```

**Code Handling:**
```python
# In route_after_supervisor
supervisor_decision = state.get("supervisor_decision")
if not supervisor_decision or not supervisor_decision.primary_agent:
    # Fallback to education
    return "education_agent"
```

---

### Edge Case 4: Execution Plan Interrupted

**Scenario:** Multi-agent plan, but 2nd agent fails

**Flow:**
```
Supervisor → Agent1 (✓) → sequence_router → Agent2 (✗ ERROR) →
  (Error response added) → END (no synthesis, partial results)
```

**Code Handling:**
```python
# In _execute_agent_node
try:
    response = agent_function(question)
except Exception as e:
    response = f"Error in {agent_type.value} agent: {str(e)}"

    # Clear execution plan to stop sequence
    execution_plan = None

return {
    "final_response": response,
    "execution_plan": None  # Stop the sequence
}
```

**Result:** Returns partial results, doesn't continue to remaining agents

---

### Edge Case 5: Web UI Memory Overflow

**Scenario:** Very long conversation (100+ messages)

**Flow:**
```
Normal flow, but state gets large → LangGraph checkpointer handles it
```

**Potential Issue:** Large message history

**Future Solution:**
```python
# In web_app/app.py or graph setup
from langchain_core.messages import trim_messages

# Trim to last 20 messages
trimmed = trim_messages(state["messages"], max_messages=20, strategy="last")
```

---

### Edge Case 6: No Execution Plan Created

**Scenario:** Supervisor decides multi-agent but doesn't create execution plan

**Flow:**
```
Supervisor → (should create plan, but doesn't) →
  route_after_supervisor → defaults to primary_agent → END
```

**Code Handling:**
```python
# In supervisor_node
if supervisor_decision.execution_mode != "single":
    # Create execution plan
    agents_queue = [supervisor_decision.primary_agent] + supervisor_decision.secondary_agents
    execution_plan = {
        "agents_queue": agents_queue,
        "current_index": 0,
        "needs_synthesis": True
    }
else:
    execution_plan = None
```

**Guarantee:** Execution plan is always created for multi-agent mode

---

## State Flow

### State Schema Through Execution

**Initial State:**
```python
{
    "messages": [{"role": "user", "content": "Question"}],
    "router_decision": None,
    "supervisor_decision": None,
    "user_context": {},
    "agent_results": {},
    "current_agent": None,
    "agents_completed": [],
    "execution_plan": None,
    "final_response": None
}
```

**After Fast Router (High Confidence):**
```python
{
    "messages": [{"role": "user", "content": "Question"}],
    "router_decision": {
        "route": "direct",
        "agent": "education",
        "confidence": 0.95,
        "reasoning": "..."
    },
    # ... rest unchanged
}
```

**After Agent Execution (Single Agent):**
```python
{
    "messages": [
        {"role": "user", "content": "Question"},
        {"role": "assistant", "content": "Answer"}
    ],
    "router_decision": {...},
    "agent_results": {"education": "Answer"},
    "current_agent": "education",
    "agents_completed": ["education"],
    "final_response": "Answer",
    "execution_plan": None  # Single agent
}
```

**After Supervisor (Multi-Agent):**
```python
{
    "messages": [...],
    "router_decision": {...},
    "supervisor_decision": {
        "primary_agent": "portfolio",
        "secondary_agents": ["market"],
        "execution_mode": "sequential",
        "reasoning": "...",
        "workflow_steps": [...]
    },
    "execution_plan": {
        "agents_queue": ["portfolio", "market"],
        "current_index": 0,
        "needs_synthesis": True
    },
    # ... rest
}
```

**During Multi-Agent (After Agent 1):**
```python
{
    "messages": [..., agent1_response],
    "agent_results": {"portfolio": "..."},
    "agents_completed": ["portfolio"],
    "current_agent": "portfolio",
    "execution_plan": {
        "agents_queue": ["portfolio", "market"],
        "current_index": 1,  # INCREMENTED
        "needs_synthesis": True
    },
    # ...
}
```

**After Synthesizer:**
```python
{
    "messages": [..., all_responses, synthesized_response],
    "agent_results": {"portfolio": "...", "market": "..."},
    "agents_completed": ["portfolio", "market"],
    "final_response": "**PORTFOLIO ANALYSIS**\n...\n**COMPREHENSIVE ANALYSIS**\n...",
    "execution_plan": {
        "current_index": 2,  # Complete
        # ...
    }
}
```

---

## Decision Points

### Decision Point 1: Fast Router Confidence

```python
if confidence >= FAST_ROUTER_CONFIDENCE_THRESHOLD:  # 0.9
    return "direct"  # Skip supervisor
else:
    return "supervisor"  # Need LLM analysis
```

**Thresholds:**
- ≥ 0.9: High confidence → Direct routing
- < 0.9: Low confidence → Supervisor

**Tuning:** Can adjust threshold in `src/orchestration/router.py`

---

### Decision Point 2: Supervisor Execution Mode

```python
if supervisor_decision.execution_mode == "single":
    execution_plan = None
    return primary_agent
else:  # "sequential" or "parallel"
    execution_plan = create_plan(...)
    return first_agent_in_queue
```

**Modes:**
- `"single"`: One agent only
- `"sequential"`: Agents run one after another
- `"parallel"`: (Future) Agents run concurrently

---

### Decision Point 3: Continue Sequence or End?

```python
def route_after_agent(state):
    if state.get("execution_plan"):
        return "sequence_router"  # Multi-agent: continue
    return "end"  # Single agent: done
```

---

### Decision Point 4: Next Agent or Synthesize?

```python
def route_sequence(state):
    plan = state["execution_plan"]
    if plan["current_index"] < len(plan["agents_queue"]):
        next_agent = plan["agents_queue"][plan["current_index"]]
        return f"{next_agent}_agent"
    else:
        return "synthesize"  # Queue complete
```

---

## Summary Table

| Scenario | Nodes Executed | Total Time | Key Characteristic |
|----------|----------------|------------|-------------------|
| High confidence single | 2 (router + agent) | ~2-3s | Fastest path |
| Low confidence single | 3 (router + supervisor + agent) | ~3-4s | +1 LLM call |
| Multi-agent (2 agents) | 7 (router + supervisor + 2 agents + 2 routers + synthesizer) | ~6-8s | Sequential processing |
| Multi-agent (3 agents) | 10 (router + supervisor + 3 agents + 3 routers + synthesizer) | ~8-12s | Full workflow |

---

## Visual Summary

```
┌────────────────────────────────────────────────────────────┐
│                    ROUTING DECISION TREE                    │
└────────────────────────────────────────────────────────────┘

                        Fast Router
                             │
                    ┌────────┴────────┐
                    │                 │
              Confidence           Confidence
                ≥ 0.9               < 0.9
                    │                 │
                    │            Supervisor
                    │                 │
                    │        ┌────────┴────────┐
                    │        │                 │
                    │    execution_         execution_
                    │    mode="single"      mode="sequential"
                    │        │                 │
                    ▼        ▼                 ▼
              ┌─────────────────┐        ┌──────────┐
              │  Single Agent   │        │ Multi-   │
              │                 │        │ Agent    │
              │  2-3 nodes      │        │ Sequence │
              │  ~2-4s          │        │          │
              │                 │        │ 7-13     │
              │  END            │        │ nodes    │
              └─────────────────┘        │ ~6-12s   │
                                        │          │
                                        │ Synth-   │
                                        │ esizer   │
                                        │          │
                                        │ END      │
                                        └──────────┘
```

---

**Created:** 2026-01-17
**Status:** Complete guide for all execution paths
**Use Case:** Understanding LangGraph orchestration flow
