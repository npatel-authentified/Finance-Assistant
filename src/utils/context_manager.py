"""
Context Window Management for AI Finance Assistant

Manages conversation context to optimize token usage and stay within LLM limits.
Uses smart trimming to keep recent messages while preserving important context.
"""

from typing import List, Dict, Any, Optional
from langchain_core.messages import trim_messages, BaseMessage, HumanMessage, AIMessage


# Configuration
DEFAULT_MAX_MESSAGES = 10  # Keep last 10 messages (5 turns)
DEFAULT_MAX_TOKENS = 4000  # Approximate token limit for context


def convert_to_dict_messages(messages: List[Any]) -> List[Dict[str, Any]]:
    """
    Convert messages to dictionary format.

    Handles both LangChain message objects and dict formats.

    Args:
        messages: List of messages (can be dicts or LangChain objects)

    Returns:
        List of message dicts with 'role' and 'content' keys
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


def trim_conversation_history(
    messages: List[Any],
    max_messages: Optional[int] = None,
    max_tokens: Optional[int] = None,
    strategy: str = "last"
) -> List[Dict[str, Any]]:
    """
    Trim conversation history to manage context window size.

    Strategies:
    - "last": Keep the most recent N messages
    - "summary": (Future) Summarize older messages, keep recent ones full
    - "relevant": (Future) Use embeddings to keep most relevant messages

    Args:
        messages: Full conversation history
        max_messages: Maximum number of messages to keep (default: 10)
        max_tokens: Maximum tokens (default: 4000) - not yet implemented
        strategy: Trimming strategy ("last" is currently supported)

    Returns:
        Trimmed message list

    Examples:
        >>> messages = [
        ...     {"role": "user", "content": "Q1"},
        ...     {"role": "assistant", "content": "A1"},
        ...     {"role": "user", "content": "Q2"},
        ...     {"role": "assistant", "content": "A2"},
        ...     {"role": "user", "content": "Q3"},
        ... ]
        >>> trimmed = trim_conversation_history(messages, max_messages=3)
        >>> len(trimmed)
        3
        >>> trimmed[0]["content"]
        'A2'
    """
    if not messages:
        return messages

    # Convert to dict format first (handles LangChain objects)
    dict_messages = convert_to_dict_messages(messages)

    max_messages = max_messages or DEFAULT_MAX_MESSAGES

    # Strategy: Keep last N messages
    if strategy == "last":
        if len(dict_messages) <= max_messages:
            return dict_messages

        # Always keep the most recent messages
        return dict_messages[-max_messages:]

    # Future: Add other strategies
    # elif strategy == "summary":
    #     return _trim_with_summary(dict_messages, max_messages)
    # elif strategy == "relevant":
    #     return _trim_by_relevance(dict_messages, max_messages)

    # Default: return converted messages
    return dict_messages


def trim_for_agent(
    messages: List[Dict[str, Any]],
    agent_type: str = "general"
) -> List[Dict[str, Any]]:
    """
    Trim messages with agent-specific context requirements.

    Different agents need different amounts of context:
    - Education: Can work with less context (focused Q&A)
    - Portfolio: Needs more context (track investments over time)
    - Goal Planning: Needs more context (long-term planning)
    - Market: Can work with less context (current market data)
    - News: Can work with less context (recent news)

    Args:
        messages: Full conversation history
        agent_type: Type of agent ("education", "portfolio", etc.)

    Returns:
        Trimmed message list appropriate for the agent

    Examples:
        >>> messages = [msg1, msg2, ..., msg20]
        >>> edu_context = trim_for_agent(messages, "education")
        >>> len(edu_context)  # Smaller context
        6
        >>> portfolio_context = trim_for_agent(messages, "portfolio")
        >>> len(portfolio_context)  # Larger context
        15
    """
    # Agent-specific context window sizes
    agent_context_sizes = {
        "education": 6,      # 3 turns - focused Q&A
        "market": 6,         # 3 turns - current market focus
        "news": 6,           # 3 turns - recent news focus
        "goal_planning": 15, # 7-8 turns - long-term planning needs history
        "portfolio": 15,     # 7-8 turns - track investments over time
        "general": 10,       # 5 turns - default
    }

    max_messages = agent_context_sizes.get(agent_type, DEFAULT_MAX_MESSAGES)
    return trim_conversation_history(messages, max_messages=max_messages)


def estimate_token_count(messages: List[Any]) -> int:
    """
    Estimate token count for message list.

    Rough estimation: 1 token ≈ 4 characters
    More accurate counting would use tiktoken library.

    Args:
        messages: Message list (dicts or LangChain objects)

    Returns:
        Estimated token count

    Examples:
        >>> messages = [{"role": "user", "content": "Hello world"}]
        >>> estimate_token_count(messages)
        3
    """
    # Convert to dict format first
    dict_messages = convert_to_dict_messages(messages)

    total_chars = sum(
        len(msg.get("content", ""))
        for msg in dict_messages
    )
    # Rough approximation: 1 token ≈ 4 characters
    # Add overhead for role/structure: +20%
    return int((total_chars / 4) * 1.2)


def should_trim_context(messages: List[Dict[str, Any]]) -> bool:
    """
    Check if context should be trimmed.

    Args:
        messages: Message list

    Returns:
        True if trimming is recommended

    Examples:
        >>> short = [{"role": "user", "content": "Hi"}] * 5
        >>> should_trim_context(short)
        False
        >>> long = [{"role": "user", "content": "Hi"}] * 30
        >>> should_trim_context(long)
        True
    """
    # Trim if more than 20 messages (10 turns)
    if len(messages) > 20:
        return True

    # Trim if estimated tokens exceed limit
    estimated_tokens = estimate_token_count(messages)
    if estimated_tokens > DEFAULT_MAX_TOKENS:
        return True

    return False


def get_context_summary(messages: List[Any]) -> str:
    """
    Generate a summary of the conversation context.

    Useful for debugging and logging.

    Args:
        messages: Message list (dicts or LangChain objects)

    Returns:
        Summary string

    Examples:
        >>> messages = [
        ...     {"role": "user", "content": "Hello"},
        ...     {"role": "assistant", "content": "Hi there!"},
        ...     {"role": "user", "content": "How are you?"}
        ... ]
        >>> summary = get_context_summary(messages)
        >>> "3 messages" in summary
        True
    """
    if not messages:
        return "Empty conversation"

    # Convert to dict format first
    dict_messages = convert_to_dict_messages(messages)

    num_messages = len(dict_messages)
    num_turns = num_messages // 2
    estimated_tokens = estimate_token_count(messages)

    user_messages = [m for m in dict_messages if m.get("role") == "user"]
    assistant_messages = [m for m in dict_messages if m.get("role") == "assistant"]

    return (
        f"{num_messages} messages ({num_turns} turns) - "
        f"~{estimated_tokens} tokens - "
        f"{len(user_messages)} user, {len(assistant_messages)} assistant"
    )


# Future: Advanced context management

def _trim_with_summary(
    messages: List[Dict[str, Any]],
    max_messages: int
) -> List[Dict[str, Any]]:
    """
    (Future) Trim older messages and replace with summary.

    Keep recent messages full, summarize older ones.

    Example:
        [Old1, Old2, Old3, Recent1, Recent2, Recent3]
        → [Summary(Old1-3), Recent1, Recent2, Recent3]
    """
    # TODO: Implement with LLM summarization
    # For now, fall back to simple trimming
    return messages[-max_messages:]


def _trim_by_relevance(
    messages: List[Dict[str, Any]],
    max_messages: int,
    current_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    (Future) Keep most relevant messages using embeddings.

    Use semantic similarity to keep messages relevant to current query.
    """
    # TODO: Implement with embeddings
    # For now, fall back to simple trimming
    return messages[-max_messages:]


# Utility functions for message format conversion

def dict_to_langchain_message(msg_dict: Dict[str, Any]) -> BaseMessage:
    """Convert dict format to LangChain message object."""
    role = msg_dict.get("role", "user")
    content = msg_dict.get("content", "")

    if role == "user":
        return HumanMessage(content=content)
    elif role == "assistant":
        return AIMessage(content=content)
    else:
        # Default to human message
        return HumanMessage(content=content)


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


# Export main functions
__all__ = [
    "convert_to_dict_messages",
    "trim_conversation_history",
    "trim_for_agent",
    "estimate_token_count",
    "should_trim_context",
    "get_context_summary",
    "dict_to_langchain_message",
    "langchain_to_dict_message",
]
