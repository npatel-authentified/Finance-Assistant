# LangChain Object Error Fix

## Error

```
'HumanMessage' object is not subscriptable
```

## Root Cause

When using LangGraph's `add_messages` reducer, messages are stored as **LangChain message objects** (HumanMessage, AIMessage), not plain dictionaries.

### The Problem

```python
# In state (from LangGraph)
messages = [
    HumanMessage(content="Hello"),  # ← LangChain object
    AIMessage(content="Hi there!")   # ← LangChain object
]

# Our code tried to do:
message["content"]  # ❌ Error! Can't subscript objects

# Should be:
message.content  # ✅ Access as attribute
```

## Solution

Updated `src/utils/context_manager.py` to automatically convert LangChain objects to dictionaries:

### New Function Added

```python
def convert_to_dict_messages(messages: List[Any]) -> List[Dict[str, Any]]:
    """
    Convert messages to dictionary format.

    Handles both LangChain message objects and dict formats.
    """
    result = []
    for msg in messages:
        if isinstance(msg, dict):
            # Already a dict
            result.append(msg)
        elif isinstance(msg, BaseMessage):
            # LangChain message object - convert to dict
            result.append(langchain_to_dict_message(msg))
        else:
            # Unknown format - try to extract content
            result.append({
                "role": "user",
                "content": str(msg)
            })
    return result
```

### Updated Functions

All these functions now convert messages automatically:

1. `trim_conversation_history()` - Converts before trimming
2. `trim_for_agent()` - Returns dict format
3. `estimate_token_count()` - Converts for counting
4. `get_context_summary()` - Converts for summary

## Files Changed

1. **src/utils/context_manager.py**
   - Added `convert_to_dict_messages()` function
   - Updated all functions to handle LangChain objects
   - Added to `__all__` exports

2. **src/orchestration/nodes.py**
   - Simplified message content extraction
   - Now relies on dict format from `trim_for_agent()`

## How It Works Now

```python
# Flow:
1. LangGraph state has: [HumanMessage(...), AIMessage(...)]

2. trim_for_agent() calls convert_to_dict_messages()
   → Returns: [{"role": "user", "content": "..."}, ...]

3. Agents receive: dict format (no LangChain objects)

4. No more 'HumanMessage' object is not subscriptable errors! ✅
```

## Test It

```bash
# Run the web UI
python web_app/app.py

# Test conversation
User: "Hello"
Bot: "Hi there!"

User: "What's your name?"
# Should work without errors ✅
```

## Technical Details

### LangChain Message Types

```python
from langchain_core.messages import (
    HumanMessage,    # User messages
    AIMessage,       # Assistant messages
    SystemMessage,   # System messages
    BaseMessage      # Base class
)
```

### Conversion Function

```python
def langchain_to_dict_message(msg: BaseMessage) -> Dict[str, Any]:
    """Convert LangChain message object to dict format."""
    if isinstance(msg, HumanMessage):
        role = "user"
    elif isinstance(msg, AIMessage):
        role = "assistant"
    else:
        role = "system"

    return {
        "role": role,
        "content": msg.content
    }
```

## Why This Happened

When we added `Annotated[List[Dict], add_messages]` to the state:

```python
# src/orchestration/types.py
class FinancialAssistantState(TypedDict):
    messages: Annotated[List[Dict[str, Any]], add_messages]  # ← This annotation
```

The `add_messages` reducer **automatically converts** dict messages to LangChain objects for internal storage. This is LangGraph's default behavior for better message handling.

**Result:** State stores LangChain objects, not dicts!

## Summary

- ✅ **Fixed:** Automatic conversion from LangChain objects to dicts
- ✅ **Transparent:** No changes needed to agent code
- ✅ **Robust:** Handles both dict and object formats
- ✅ **Future-proof:** Works with any LangChain message type

**Status:** Error fixed! Ready to test. 🎉

---

**Date:** 2026-01-17
**Error:** 'HumanMessage' object is not subscriptable
**Fix:** Auto-conversion in context_manager.py
**Files Changed:** 2 (context_manager.py, nodes.py)
