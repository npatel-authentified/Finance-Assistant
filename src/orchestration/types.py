"""
Type definitions for multi-agent routing and orchestration.

Defines enums, models, and state schemas used across the orchestration layer.
"""

from enum import Enum
from typing import TypedDict, List, Dict, Any, Literal, Optional, Annotated
from pydantic import BaseModel, Field
from langgraph.graph import add_messages


class AgentType(Enum):
    """Available specialized agents in the system."""

    EDUCATION = "education"           # ques_ans.py - General financial education (RAG)
    GOAL_PLANNING = "goal_planning"   # goal_planning.py - Financial goal planning
    PORTFOLIO = "portfolio"           # portfolio_analysis.py - Portfolio analysis
    MARKET = "market"                 # market_analysis.py - Market analysis
    NEWS = "news"                     # news_synthesizer.py - Investment research


class RouterDecision(BaseModel):
    """
    Fast router decision output.

    Represents the decision made by the rule-based fast router.
    """

    route: Literal["direct", "supervisor"] = Field(
        description="Whether to route directly to an agent or use supervisor"
    )
    agent: Optional[AgentType] = Field(
        default=None,
        description="Which agent to use (if direct routing)"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score for this routing decision (0.0-1.0)"
    )
    reasoning: str = Field(
        description="Explanation of why this routing decision was made"
    )
    context_hints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context to pass to supervisor (e.g., keyword scores)"
    )


class SupervisorDecision(BaseModel):
    """
    Supervisor routing decision output.

    Represents the decision made by the LLM-based supervisor for complex/ambiguous questions.
    """

    primary_agent: AgentType = Field(
        description="Main agent that should handle this request"
    )
    secondary_agents: List[AgentType] = Field(
        default_factory=list,
        description="Additional agents to call (for multi-agent scenarios)"
    )
    execution_mode: Literal["single", "sequential", "parallel"] = Field(
        default="single",
        description="How to execute multiple agents: single, sequential, or parallel"
    )
    reasoning: str = Field(
        description="Explanation of routing decision and strategy"
    )
    workflow_steps: List[str] = Field(
        default_factory=list,
        description="Ordered steps for sequential execution (if applicable)"
    )


class UserContext(TypedDict, total=False):
    """
    Persistent user context across conversation.

    Tracks user state to improve routing decisions.
    """

    has_portfolio: bool              # Whether user owns stocks
    portfolio_value: Optional[float] # Approximate portfolio value
    active_goals: List[int]          # Goal IDs from goal planning agent
    risk_tolerance: Optional[str]    # low, medium, high
    investment_stage: str            # "potential", "current", "unknown"
    last_agent: Optional[str]        # Last agent used in conversation


class AgentResults(TypedDict, total=False):
    """
    Results from each agent (for multi-agent scenarios).

    Allows agents to share data and build on each other's outputs.
    """

    education: Optional[str]         # Education agent result
    goal_planning: Optional[Dict]    # Goal planning agent result
    portfolio: Optional[Dict]        # Portfolio analysis result
    market: Optional[Dict]           # Market analysis result
    news: Optional[Dict]             # News synthesizer result


class ExecutionPlan(TypedDict, total=False):
    """
    Execution plan for sequential multi-agent workflows.

    Tracks which agents need to execute and the current position in the queue.
    """

    agents_queue: List[AgentType]    # Ordered list of agents to execute
    current_index: int               # Current position in queue (0-indexed)
    needs_synthesis: bool            # Whether to synthesize at the end


class FinancialAssistantState(TypedDict):
    """
    LangGraph state for the financial assistant orchestration.

    This state flows through the entire routing and execution workflow.

    Note: The 'messages' field uses Annotated with add_messages reducer.
    This means nodes can return new messages and they'll be automatically
    appended to the conversation history, rather than replacing it.
    """

    # Core conversation (with reducer for automatic appending)
    messages: Annotated[List[Dict[str, Any]], add_messages]

    # Routing metadata
    router_decision: Optional[RouterDecision]
    supervisor_decision: Optional[SupervisorDecision]

    # User context (persistent across conversation)
    user_context: UserContext

    # Inter-agent communication
    agent_results: AgentResults

    # Workflow control
    current_agent: Optional[str]
    agents_completed: List[str]
    execution_plan: Optional[ExecutionPlan]  # Sequential multi-agent execution tracking
    final_response: Optional[str]


class RoutingMetrics(BaseModel):
    """
    Metrics for monitoring routing performance.

    Track these to optimize routing decisions over time.
    """

    total_requests: int = 0
    fast_path_hits: int = 0           # Questions routed directly
    supervisor_path_hits: int = 0     # Questions sent to supervisor
    fast_path_accuracy: float = 0.0   # % of correct fast path routes
    supervisor_accuracy: float = 0.0  # % of correct supervisor routes
    avg_latency_fast: float = 0.0     # Average latency for fast path (ms)
    avg_latency_supervisor: float = 0.0  # Average latency for supervisor (ms)
    user_override_rate: float = 0.0   # % of times user corrected routing

    def fast_path_hit_rate(self) -> float:
        """Calculate percentage of requests using fast path."""
        if self.total_requests == 0:
            return 0.0
        return (self.fast_path_hits / self.total_requests) * 100

    def supervisor_path_hit_rate(self) -> float:
        """Calculate percentage of requests using supervisor."""
        if self.total_requests == 0:
            return 0.0
        return (self.supervisor_path_hits / self.total_requests) * 100
