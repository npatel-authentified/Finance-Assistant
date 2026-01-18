# Understanding `Annotated` in LangGraph State

## TL;DR

**We just updated `FinancialAssistantState` to use `Annotated[List, add_messages]` for the `messages` field.**

This is the **recommended pattern** for LangGraph chat applications. It makes message handling cleaner and more robust.

## What is `Annotated`?

`Annotated` is used in LangGraph to specify **reducers** - functions that control how state updates are merged when nodes modify the state.

### Without Annotated (Replacement Semantics)

```python
class MyState(TypedDict):
    messages: List[Dict]  # Last write wins
    count: int            # Last write wins
```

**Behavior:**
```python
# Node A returns:
{"messages": [{"role": "user", "content": "Hello"}]}

# Node B returns:
{"messages": [{"role": "assistant", "content": "Hi"}]}

# Final state:
{"messages": [{"role": "assistant", "content": "Hi"}]}  # Node B overwrote Node A!
```

### With Annotated (Custom Merge Logic)

```python
from typing import Annotated
from langgraph.graph import add_messages

class MyState(TypedDict):
    messages: Annotated[List[Dict], add_messages]  # Appends instead of replacing
    count: int  # Still replacement
```

**Behavior:**
```python
# Node A returns:
{"messages": [{"role": "user", "content": "Hello"}]}

# Node B returns:
{"messages": [{"role": "assistant", "content": "Hi"}]}

# Final state:
{"messages": [
    {"role": "user", "content": "Hello"},      # From Node A
    {"role": "assistant", "content": "Hi"}     # From Node B - APPENDED!
]}
```

## Why Use `add_messages` for Chat Apps?

The `add_messages` reducer is **specifically designed for conversation history**:

1. **Appends new messages** instead of replacing
2. **Deduplicates** messages with the same ID
3. **Handles message types** (HumanMessage, AIMessage, SystemMessage, etc.)
4. **Preserves order** of conversation

### Before (Manual Appending)

```python
def my_agent_node(state: FinancialAssistantState):
    messages = state["messages"]

    # Manually append
    new_messages = messages + [AIMessage(content="Response")]

    return {
        "messages": new_messages,  # Return entire list
        "other_field": "value"
    }
```

Problems:
- ❌ Verbose - need to get messages, append, return full list
- ❌ Easy to forget and accidentally replace messages
- ❌ Doesn't handle deduplication

### After (With add_messages Reducer)

```python
def my_agent_node(state: FinancialAssistantState):
    # Just return new message - reducer handles appending!
    return {
        "messages": [AIMessage(content="Response")],  # Just the new message
        "other_field": "value"
    }
```

Benefits:
- ✅ Cleaner - just return new messages
- ✅ Reducer automatically appends
- ✅ Handles deduplication
- ✅ More LangGraph idiomatic

## Our Current Implementation

### What We Changed

**File:** `src/orchestration/types.py`

```python
# Before:
class FinancialAssistantState(TypedDict):
    messages: List[Dict[str, Any]]  # Replacement semantics

# After:
class FinancialAssistantState(TypedDict):
    messages: Annotated[List[Dict[str, Any]], add_messages]  # Append semantics
```

### How It Works Now

**Before (manual appending):**
```python
def agent_executor_node(state):
    messages = state["messages"]
    response = agent.invoke({"messages": messages})
    new_messages = messages + [AIMessage(content=response)]  # Manual append
    return {"messages": new_messages}
```

**After (with reducer):**
```python
def agent_executor_node(state):
    messages = state["messages"]
    response = agent.invoke({"messages": messages})
    return {"messages": [AIMessage(content=response)]}  # Reducer appends automatically
```

**Both produce the same result**, but the second is cleaner!

## When to Use Annotated?

### Use Annotated When:

1. **Messages field** - Always use `add_messages` reducer
   ```python
   messages: Annotated[List[Dict], add_messages]
   ```

2. **Lists that accumulate** - Use custom reducer or `operator.add`
   ```python
   from operator import add

   results: Annotated[List[str], add]  # Concatenates lists
   ```

3. **Numbers that accumulate** - Use `operator.add`
   ```python
   from operator import add

   total_cost: Annotated[float, add]  # Sums numbers
   ```

4. **Custom merge logic** - Define your own reducer
   ```python
   def merge_dicts(left: dict, right: dict) -> dict:
       return {**left, **right}

   metadata: Annotated[Dict, merge_dicts]
   ```

### Don't Use Annotated When:

1. **Last write wins is correct** - Most fields
   ```python
   current_agent: Optional[str]  # Only one agent at a time
   final_response: Optional[str]  # Only one final answer
   ```

2. **Single-writer fields** - Only one node updates it
   ```python
   router_decision: Optional[RouterDecision]  # Only router writes
   ```

## Common Reducers

### Built-in LangGraph Reducers

```python
from langgraph.graph import add_messages

# For conversation history
messages: Annotated[List[Dict], add_messages]
```

### Python Operator Reducers

```python
from operator import add

# Concatenate lists
results: Annotated[List[str], add]  # [1,2] + [3,4] = [1,2,3,4]

# Sum numbers
total: Annotated[int, add]  # 5 + 3 = 8
```

### Custom Reducers

```python
def merge_agent_results(left: dict, right: dict) -> dict:
    """Merge results, keeping most recent for each agent."""
    return {**left, **right}

agent_results: Annotated[Dict[str, Any], merge_agent_results]
```

## Examples from Our Codebase

### ✅ Using Annotated (Recommended)

```python
class FinancialAssistantState(TypedDict):
    # Multiple nodes add messages - use reducer
    messages: Annotated[List[Dict[str, Any]], add_messages]

    # Only one node writes these - no reducer needed
    router_decision: Optional[RouterDecision]
    final_response: Optional[str]
```

### Simpler Node Code

**Router node:**
```python
def fast_router_node(state):
    decision = make_routing_decision(state["messages"])

    # No manual message handling - just set routing metadata
    return {
        "router_decision": decision
    }
```

**Agent node:**
```python
def education_agent_node(state):
    response = agent.invoke(state["messages"])

    # Just return new message - reducer appends it
    return {
        "messages": [AIMessage(content=response)],
        "current_agent": "education"
    }
```

**Synthesizer node:**
```python
def synthesizer_node(state):
    synthesis = synthesize_results(state["agent_results"])

    # Clean - just return the final message
    return {
        "messages": [AIMessage(content=synthesis)],
        "final_response": synthesis
    }
```

## Migration Path (If We Want to Simplify Further)

Our nodes currently do manual appending:
```python
new_messages = messages + [AIMessage(content=response)]
return {"messages": new_messages}
```

We can simplify to:
```python
return {"messages": [AIMessage(content=response)]}
```

**Both work**, but the second is cleaner. The reducer handles the appending.

## Best Practices

1. **Always use `add_messages` for conversation history**
   ```python
   messages: Annotated[List[Dict], add_messages]
   ```

2. **Use descriptive reducer names**
   ```python
   def merge_agent_outputs(left, right):
       return {**left, **right}

   results: Annotated[Dict, merge_agent_outputs]
   ```

3. **Document reducer behavior**
   ```python
   # Lists are concatenated, newer results override older ones
   intermediate_steps: Annotated[List[Tuple], add]
   ```

4. **Keep it simple** - Don't use reducers where last-write-wins is fine
   ```python
   current_step: str  # Only one current step - no reducer needed
   ```

## Debugging Tips

### See What the Reducer Does

```python
from langgraph.graph import add_messages

# Test the reducer
old_messages = [{"role": "user", "content": "Hello"}]
new_messages = [{"role": "assistant", "content": "Hi"}]

result = add_messages(old_messages, new_messages)
print(result)
# [{"role": "user", "content": "Hello"},
#  {"role": "assistant", "content": "Hi"}]
```

### Common Issues

**Issue 1: Messages not persisting**
```python
# Wrong - messages field not annotated
messages: List[Dict]  # Gets replaced each time

# Right - use add_messages
messages: Annotated[List[Dict], add_messages]
```

**Issue 2: Duplicate messages**
```python
# Nodes shouldn't manually append AND use reducer
# Wrong:
new_messages = state["messages"] + [new_msg]
return {"messages": new_messages}  # Reducer will append to this!

# Right:
return {"messages": [new_msg]}  # Let reducer handle appending
```

## Summary

| Aspect | Without Annotated | With Annotated |
|--------|------------------|----------------|
| Merge behavior | Last write wins | Custom (e.g., append) |
| For messages | Manual appending | Automatic appending |
| Code verbosity | More verbose | Cleaner |
| Error prone | Easy to forget to append | Reducer handles it |
| LangGraph pattern | ❌ Not idiomatic | ✅ Recommended |

## Updated State Definition

Our final `FinancialAssistantState`:

```python
from typing import Annotated
from langgraph.graph import add_messages

class FinancialAssistantState(TypedDict):
    # With reducer - appends messages automatically
    messages: Annotated[List[Dict[str, Any]], add_messages]

    # Without reducer - last write wins (correct for these)
    router_decision: Optional[RouterDecision]
    supervisor_decision: Optional[SupervisorDecision]
    user_context: UserContext
    agent_results: AgentResults
    current_agent: Optional[str]
    agents_completed: List[str]
    execution_plan: Optional[ExecutionPlan]
    final_response: Optional[str]
```

This is the **recommended pattern** for LangGraph chat applications!

---

**References:**
- [LangGraph State Documentation](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- [LangGraph add_messages API](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.message.add_messages)

**Date:** 2026-01-17
**Status:** ✅ Implemented in `src/orchestration/types.py`
