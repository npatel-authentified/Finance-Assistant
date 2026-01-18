"""
Multi-Agent Orchestration Layer

This module provides intelligent routing between specialized financial agents
using a Smart Router + Supervisor architecture with LangGraph.

Components:
- types: Type definitions for routing decisions and state
- router: Fast rule-based routing for common questions (80%)
- supervisor: LLM-based routing for ambiguous questions (20%)
- nodes: LangGraph node implementations
- graph: LangGraph StateGraph workflow
"""

from .types import (
    AgentType,
    RouterDecision,
    SupervisorDecision,
    FinancialAssistantState,
    ExecutionPlan,
)
from .router import fast_route, DIRECT_ROUTE_THRESHOLD
from .supervisor import supervisor_route, create_supervisor_agent
from .graph import (
    create_financial_assistant_graph,
    create_app_with_memory,
    invoke_with_question,
    stream_with_question,
    visualize_graph,
)

__all__ = [
    # Types
    "AgentType",
    "RouterDecision",
    "SupervisorDecision",
    "FinancialAssistantState",
    "ExecutionPlan",
    # Router
    "fast_route",
    "DIRECT_ROUTE_THRESHOLD",
    # Supervisor
    "supervisor_route",
    "create_supervisor_agent",
    # LangGraph
    "create_financial_assistant_graph",
    "create_app_with_memory",
    "invoke_with_question",
    "stream_with_question",
    "visualize_graph",
]
