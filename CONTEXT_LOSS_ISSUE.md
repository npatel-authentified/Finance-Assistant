# Context Loss Issue - Root Cause & Solution

## 🔴 The Problem

Your agents are losing conversation context even though LangGraph checkpointing is working correctly.

## 🔍 Root Cause Analysis

### What's Happening

**File:** `src/orchestration/nodes.py` (line 203-208)

```python
def _execute_agent_node(state, agent_type, agent_func):
    # Get the question
    messages = state.get("messages", [])
    last_message = messages[-1]
    question = last_message["content"]  # ❌ Only extracting last question!

    # Execute agent
    response = agent_func(question, verbose=False)  # ❌ Only passing last question!
```

**The Issue:**
- LangGraph checkpointer **IS** saving full message history ✅
- State **DOES** contain all previous messages ✅
- BUT agents are **ONLY** receiving the last question ❌

### Example of the Problem

**Conversation:**
```
User: "My name is Alice"
Bot: "Nice to meet you, Alice!"

User: "What's my name?"
```

**What the agent sees:**
```python
# ❌ CURRENT (WRONG):
agent_func("What's my name?")  # No context!

# ✅ SHOULD BE:
agent_func([
    {"role": "user", "content": "My name is Alice"},
    {"role": "assistant", "content": "Nice to meet you, Alice!"},
    {"role": "user", "content": "What's my name?"}
])
```

**Result:**
```
Bot: "I don't have information about your name."  ❌
```

Because the agent only sees "What's my name?" without context!

---

## 📊 Full Diagnosis

### Layer 1: Web UI ✅ WORKING

**File:** `web_app/app.py` (line 108-111)

```python
for chunk in app.stream(
    {
        "messages": [{"role": "user", "content": message}],  # ✅ Correct
    },
    config,
    stream_mode="updates",
):
```

**Status:** ✅ Correctly sends only new message
**Why it works:** LangGraph's `add_messages` reducer appends to checkpointed history

---

### Layer 2: LangGraph State ✅ WORKING

**File:** `src/orchestration/types.py` (line 130)

```python
class FinancialAssistantState(TypedDict):
    messages: Annotated[List[Dict[str, Any]], add_messages]  # ✅ Correct
```

**Status:** ✅ Reducer properly appends messages
**Why it works:** `add_messages` automatically merges new messages with checkpointed history

---

### Layer 3: Checkpointer ✅ WORKING

**File:** `src/orchestration/graph.py` (line 186)

```python
def create_app_with_memory():
    memory = MemorySaver()  # ✅ Correct
    return create_financial_assistant_graph(checkpointer=memory)
```

**Status:** ✅ Checkpointer saves and loads state correctly
**Proof:** State contains full message history

---

### Layer 4: Agent Invocation ❌ BROKEN

**File:** `src/orchestration/nodes.py` (line 203-208)

```python
def _execute_agent_node(state, agent_type, agent_func):
    messages = state.get("messages", [])  # ✅ Full history is HERE
    last_message = messages[-1]
    question = last_message["content"]    # ❌ Extract only last question

    response = agent_func(question, verbose=False)  # ❌ Pass only last question
```

**Status:** ❌ **THIS IS THE BUG**
**Why it fails:** Agents receive single string, not full conversation

---

### Layer 5: Agent Functions ❌ NOT DESIGNED FOR CONTEXT

**Files:** `src/agents/*.py`

```python
# ❌ CURRENT SIGNATURE:
def ask_question(question: str, verbose: bool = True):
    # Agent only receives: "What's my name?"
    # No access to: "My name is Alice"
```

**Status:** ❌ Agent functions need to accept full message history
**Why it fails:** Signature only accepts single question string

---

## 🛠️ The Solution

We need to update agents to receive and use full message history.

### Option 1: Update All Agents (Recommended)

**Change agent signatures to accept messages:**

```python
# BEFORE:
def ask_question(question: str, verbose: bool = True):
    # Only sees last question
    ...

# AFTER:
def ask_question(messages: List[Dict[str, Any]], verbose: bool = True):
    # Sees full conversation history
    # Can extract last question if needed:
    last_question = messages[-1]["content"]

    # Pass full messages to LangChain agent
    agent_executor.invoke({"messages": messages})
```

### Option 2: Quick Fix (Pass full messages in nodes.py)

**Update `_execute_agent_node`:**

```python
def _execute_agent_node(state, agent_type, agent_func):
    messages = state.get("messages", [])

    # ✅ Pass full message history instead of just last question
    response = agent_func(messages, verbose=False)  # Changed from question to messages
```

**Then update each agent to handle messages list:**

```python
def ask_question(messages, verbose=True):
    # Extract last question for backward compatibility
    if isinstance(messages, str):
        # Old behavior: single question
        question = messages
    else:
        # New behavior: full message history
        question = messages[-1]["content"]

    # Use the agent executor with full messages
    result = agent_executor.invoke({"messages": messages})
    return result["output"]
```

---

## 📝 Step-by-Step Fix

### Step 1: Update nodes.py

**File:** `src/orchestration/nodes.py`

```python
def _execute_agent_node(
    state: FinancialAssistantState,
    agent_type: AgentType,
    agent_func
) -> Dict[str, Any]:
    """Execute an agent with full conversation context."""

    # Get full message history
    messages = state.get("messages", [])

    # ✅ NEW: Pass full messages, not just last question
    response = agent_func(messages, verbose=False)

    # Rest of the function unchanged...
```

### Step 2: Update Each Agent

**Example:** `src/agents/ques_ans.py`

```python
def ask_question(messages, verbose: bool = True):
    """
    Ask a financial education question with full conversation context.

    Args:
        messages: Full conversation history [{"role": "user", "content": "..."}, ...]
        verbose: Whether to print execution details

    Returns:
        Agent's response string
    """
    # Handle both old (string) and new (list) formats
    if isinstance(messages, str):
        # Backward compatibility: convert to message format
        messages = [{"role": "user", "content": messages}]

    # Create agent executor
    agent = create_finance_assistant()

    # Invoke with full message history
    result = agent.invoke(
        {"messages": messages},
        config={"recursion_limit": 50}
    )

    return result["output"]
```

**Repeat for all agents:**
- `src/agents/goal_planning.py`
- `src/agents/portfolio_analysis.py`
- `src/agents/market_analysis.py`
- `src/agents/news_synthesizer.py`

---

## 🧪 Testing the Fix

### Test Conversation

```python
# Test 1: Context preservation
Q1: "My name is Alice"
A1: "Nice to meet you, Alice!"

Q2: "What's my name?"
A2: "Your name is Alice!"  ✅ (Should work after fix)

# Test 2: Portfolio context
Q1: "I have a portfolio with 60% tech stocks"
A1: "I see you have a tech-heavy portfolio..."

Q2: "Should I diversify more?"
A2: "Given your 60% tech allocation, yes..."  ✅ (References previous context)

# Test 3: Multi-turn financial advice
Q1: "I want to save for retirement"
A1: "Let's create a retirement plan..."

Q2: "I'm 30 years old"
A2: "At 30, you have 35+ years until retirement..."  ✅ (Remembers goal)

Q3: "How much should I save monthly?"
A3: "For your retirement goal at age 30..."  ✅ (Combines both contexts)
```

---

## 📊 Verification Checklist

After implementing the fix, verify:

- [ ] Agents receive full message list, not just last question
- [ ] Agent functions accept `messages` parameter
- [ ] LangChain agent executors invoked with full message history
- [ ] Test: "My name is X" → "What's my name?" → Bot responds with X
- [ ] Test: Multi-turn conversation maintains context
- [ ] Test: Clear Chat starts fresh conversation
- [ ] No errors in console/logs

---

## 🎯 Why This Happened

The original implementation was designed for **single-turn Q&A**:
- Ask question → Get answer → Done

But we added **multi-turn conversation** without updating agents:
- Turn 1 → Turn 2 → Turn 3 (each needs context)

The checkpointing layer was added ✅, but agent invocation wasn't updated ❌.

---

## 🔧 Alternative: Use LangChain's Memory

**Option 3: Let LangChain handle memory** (if agents use LangChain agents)

```python
from langchain.memory import ConversationBufferMemory

# In agent creation
memory = ConversationBufferMemory(return_messages=True)

agent = create_react_agent(
    llm=llm,
    tools=tools,
    memory=memory  # Agent manages its own memory
)
```

**Pros:** Built-in memory management
**Cons:** Duplicates LangGraph's checkpointing

**Recommendation:** Stick with Option 1 or 2 - use LangGraph's state management

---

## 📈 Expected Behavior After Fix

### Before Fix:
```
State: [Q1, A1, Q2]
         ↓
Agent sees: Q2 only
         ↓
No context! ❌
```

### After Fix:
```
State: [Q1, A1, Q2]
         ↓
Agent sees: [Q1, A1, Q2]
         ↓
Full context! ✅
```

---

## 🚀 Implementation Priority

**High Priority:**
1. Update `_execute_agent_node` to pass `messages` not `question`
2. Update `ask_question` in `ques_ans.py` (education agent - most used)
3. Test with simple conversation

**Medium Priority:**
4. Update remaining 4 agents (goal, portfolio, market, news)
5. Add backward compatibility checks

**Low Priority:**
6. Update agent docstrings
7. Add unit tests for context preservation

---

## 💡 Key Insight

**The checkpointing system is working perfectly!**

The bug is in the **"last mile"** - we're not using the full message history that's correctly stored in state.

Think of it like:
- 📦 Package delivered to your door (LangGraph state) ✅
- 🚪 But you only open the top layer (last message) ❌
- 📄 Need to look at the whole package (all messages) ✅

---

**Root Cause:** Agent invocation only passes last question, not full message history
**Impact:** Agents can't maintain conversation context
**Solution:** Pass full `messages` list to agent functions
**Complexity:** Medium (need to update 5 agent files + 1 node file)
**Testing:** Critical - verify multi-turn conversations work

---

**Created:** 2026-01-17
**Status:** Root cause identified, solution provided
**Next Step:** Implement Option 1 or Option 2
