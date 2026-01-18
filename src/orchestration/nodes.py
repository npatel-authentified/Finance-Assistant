"""
LangGraph Node Implementations

Each node is a function that takes state and returns updated state.
Nodes are the building blocks of the LangGraph workflow.
"""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage

from .router import fast_route
from .supervisor import supervisor_route
from .types import FinancialAssistantState, AgentType, ExecutionPlan
from src.utils.context_manager import trim_for_agent, get_context_summary

# Import all specialized agents
from src.agents.ques_ans import ask_question as ask_education
from src.agents.goal_planning import ask_question as ask_goal_planning
from src.agents.portfolio_analysis import ask_question as ask_portfolio
from src.agents.market_analysis import ask_question as ask_market
from src.agents.news_synthesizer import ask_question as ask_news


# Agent dispatcher
AGENT_FUNCTIONS = {
    AgentType.EDUCATION: ask_education,
    AgentType.GOAL_PLANNING: ask_goal_planning,
    AgentType.PORTFOLIO: ask_portfolio,
    AgentType.MARKET: ask_market,
    AgentType.NEWS: ask_news,
}


def fast_router_node(state: FinancialAssistantState) -> Dict[str, Any]:
    """
    Fast router node - uses pattern matching and keyword scoring.

    Decides whether to route directly to an agent or use supervisor.

    Args:
        state: Current workflow state

    Returns:
        Updated state with router_decision
    """
    # Get the last user message
    messages = state.get("messages", [])
    if not messages:
        return state

    last_message = messages[-1]
    question = last_message["content"] if isinstance(last_message, dict) else last_message.content

    # Get user context for routing
    context = {
        "user_context": state.get("user_context", {}),
        "last_agent": state.get("current_agent"),
    }

    # Fast route
    router_decision = fast_route(question, context)

    # Update state
    return {
        **state,
        "router_decision": router_decision,
    }


def supervisor_node(state: FinancialAssistantState) -> Dict[str, Any]:
    """
    Supervisor node - uses LLM for intelligent routing.

    Handles ambiguous questions and multi-agent decisions.
    For multi-agent scenarios, initializes the execution plan.

    Args:
        state: Current workflow state

    Returns:
        Updated state with supervisor_decision and execution_plan (if multi-agent)
    """
    # Get the last user message
    messages = state.get("messages", [])
    last_message = messages[-1]
    question = last_message["content"] if isinstance(last_message, dict) else last_message.content

    # Get context and hints from fast router
    context = {
        "user_context": state.get("user_context", {}),
        "last_agent": state.get("current_agent"),
    }

    router_decision = state.get("router_decision")
    hints = router_decision.context_hints if router_decision else {}

    # Get supervisor decision
    supervisor_decision = supervisor_route(question, context, hints)

    # Initialize execution plan for multi-agent scenarios
    execution_plan = None
    if supervisor_decision.execution_mode in ["sequential", "parallel"]:
        # Create execution plan (sequential only for now)
        agents_to_execute = [supervisor_decision.primary_agent] + supervisor_decision.secondary_agents
        execution_plan = {
            "agents_queue": agents_to_execute,
            "current_index": 0,  # Will start with first agent
            "needs_synthesis": True,  # Always synthesize multi-agent results
        }

    # Update state
    return {
        **state,
        "supervisor_decision": supervisor_decision,
        "execution_plan": execution_plan,
    }


def education_agent_node(state: FinancialAssistantState) -> Dict[str, Any]:
    """
    Education agent node - handles general financial education questions.

    Args:
        state: Current workflow state

    Returns:
        Updated state with agent response
    """
    return _execute_agent_node(state, AgentType.EDUCATION, ask_education)


def goal_planning_agent_node(state: FinancialAssistantState) -> Dict[str, Any]:
    """
    Goal planning agent node - handles financial goal planning.

    Args:
        state: Current workflow state

    Returns:
        Updated state with agent response
    """
    return _execute_agent_node(state, AgentType.GOAL_PLANNING, ask_goal_planning)


def portfolio_agent_node(state: FinancialAssistantState) -> Dict[str, Any]:
    """
    Portfolio analysis agent node - analyzes investment portfolios.

    Args:
        state: Current workflow state

    Returns:
        Updated state with agent response
    """
    return _execute_agent_node(state, AgentType.PORTFOLIO, ask_portfolio)


def market_agent_node(state: FinancialAssistantState) -> Dict[str, Any]:
    """
    Market analysis agent node - analyzes market conditions.

    Args:
        state: Current workflow state

    Returns:
        Updated state with agent response
    """
    return _execute_agent_node(state, AgentType.MARKET, ask_market)


def news_agent_node(state: FinancialAssistantState) -> Dict[str, Any]:
    """
    News synthesizer agent node - investment research.

    Args:
        state: Current workflow state

    Returns:
        Updated state with agent response
    """
    return _execute_agent_node(state, AgentType.NEWS, ask_news)


def _execute_agent_node(
    state: FinancialAssistantState,
    agent_type: AgentType,
    agent_func
) -> Dict[str, Any]:
    """
    Helper function to execute an agent and update state.

    Handles both single-agent and sequential multi-agent execution.
    For sequential execution, advances the execution plan after completing the agent.

    Args:
        state: Current workflow state
        agent_type: Type of agent being executed
        agent_func: Agent function to call

    Returns:
        Updated state with agent response and updated execution plan
    """
    # Get full message history
    messages = state.get("messages", [])

    # Trim context to appropriate size for this agent
    # Different agents need different amounts of context
    trimmed_messages = trim_for_agent(messages, agent_type=agent_type.value)

    # Log context for debugging (optional)
    # print(f"[{agent_type.value}] Context: {get_context_summary(trimmed_messages)}")

    # Execute agent with trimmed conversation history (suppress verbose output)
    response = agent_func(trimmed_messages, verbose=False)

    # Update state
    agent_results = state.get("agent_results", {})
    agent_results[agent_type.value] = response

    agents_completed = state.get("agents_completed", [])
    agents_completed.append(agent_type.value)

    # Add AI message to conversation
    new_messages = messages + [AIMessage(content=response)]

    # Extract last question for user context update
    # trimmed_messages are already dicts (converted by trim_for_agent)
    last_message = trimmed_messages[-1] if trimmed_messages else {"content": ""}
    last_question = last_message.get("content", "")

    # Update user context based on agent used
    user_context = state.get("user_context", {})
    user_context = _update_user_context(last_question, agent_type, user_context)

    # Check if this is part of a sequential execution plan
    execution_plan = state.get("execution_plan")
    if execution_plan:
        # Advance to next agent in queue
        current_index = execution_plan.get("current_index", 0)
        execution_plan = {
            **execution_plan,
            "current_index": current_index + 1,
        }

    return {
        **state,
        "messages": new_messages,
        "agent_results": agent_results,
        "agents_completed": agents_completed,
        "current_agent": agent_type.value,
        "user_context": user_context,
        "execution_plan": execution_plan,
        "final_response": response,
    }


def sequence_router_node(state: FinancialAssistantState) -> Dict[str, Any]:
    """
    Sequence router node - lightweight routing for sequential multi-agent execution.

    This node doesn't do any work - it just passes state through.
    The routing logic is in the conditional edge function (route_sequence).

    This keeps the graph clean and linear instead of a fully-connected mesh.

    Args:
        state: Current workflow state

    Returns:
        Unchanged state (routing is done by edges, not this node)
    """
    # This node is a pure router - it doesn't modify state
    # All routing logic is in the route_sequence function
    return state


def synthesizer_node(state: FinancialAssistantState) -> Dict[str, Any]:
    """
    Synthesizer node - combines results from multiple agents.

    Creates a coherent response from multiple agent outputs.

    Args:
        state: Current workflow state

    Returns:
        Updated state with synthesized response
    """
    agent_results = state.get("agent_results", {})

    if len(agent_results) == 1:
        # Single agent - just return the response
        final_response = list(agent_results.values())[0]
    else:
        # Multiple agents - combine results
        final_response = _synthesize_multi_agent_results(agent_results)

    # Add final AI message
    messages = state.get("messages", [])
    new_messages = messages + [AIMessage(content=final_response)]

    return {
        **state,
        "messages": new_messages,
        "final_response": final_response,
    }


def _synthesize_multi_agent_results(agent_results: Dict[str, str]) -> str:
    """
    Synthesize results from multiple agents into coherent response.

    For Phase 2, this is simple concatenation.
    TODO: Use LLM to intelligently synthesize in Phase 3.

    Args:
        agent_results: Dict of {agent_name: response}

    Returns:
        Combined response string
    """
    parts = []

    for agent_name, result in agent_results.items():
        parts.append(f"**{agent_name.upper()} ANALYSIS**")
        parts.append("=" * 70)
        parts.append(result)
        parts.append("")

    # Add summary
    parts.append("=" * 70)
    parts.append("**COMPREHENSIVE ANALYSIS**")
    parts.append("=" * 70)
    parts.append(
        f"Based on the analysis from {len(agent_results)} specialized agents above, "
        f"you now have a complete answer to your question."
    )

    return "\n".join(parts)


def _update_user_context(
    question: str,
    agent_type: AgentType,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update user context based on question and agent interaction.

    Args:
        question: User's question
        agent_type: Agent that handled the question
        user_context: Current user context

    Returns:
        Updated user context
    """
    question_lower = question.lower()

    # Detect if user has portfolio
    if agent_type == AgentType.PORTFOLIO:
        user_context["has_portfolio"] = True
        user_context["investment_stage"] = "current"

    # Detect investment stage
    if agent_type == AgentType.NEWS:
        if "should i invest" in question_lower or "thinking about investing" in question_lower:
            user_context["investment_stage"] = "potential"

    # Track goals (simplified - in production, would get actual goal IDs)
    if agent_type == AgentType.GOAL_PLANNING:
        if "create" in question_lower or "new goal" in question_lower:
            if "active_goals" not in user_context:
                user_context["active_goals"] = []
            # Would append actual goal ID here

    return user_context


# Routing functions for conditional edges

def route_after_fast_router(state: FinancialAssistantState) -> str:
    """
    Routing function after fast router.

    Decides whether to go directly to an agent or use supervisor.

    Args:
        state: Current workflow state

    Returns:
        Next node name
    """
    router_decision = state.get("router_decision")

    if not router_decision or router_decision.route == "supervisor":
        return "supervisor"

    # Direct routing to specific agent
    agent_type = router_decision.agent
    return f"{agent_type.value}_agent"


def route_after_supervisor(state: FinancialAssistantState) -> str:
    """
    Routing function after supervisor.

    For single-agent scenarios, routes directly to the agent.
    For multi-agent scenarios, creates an execution plan and routes to the first agent.

    Args:
        state: Current workflow state

    Returns:
        Next node name
    """
    supervisor_decision = state.get("supervisor_decision")

    if not supervisor_decision:
        # Fallback to education
        return "education_agent"

    # Check execution mode
    if supervisor_decision.execution_mode == "single":
        # Single agent - route directly
        agent_type = supervisor_decision.primary_agent
        return f"{agent_type.value}_agent"
    else:
        # Multi-agent (sequential or parallel) - create execution plan
        # For now, we implement sequential only (parallel will be Phase 2)
        agents_to_execute = [supervisor_decision.primary_agent] + supervisor_decision.secondary_agents

        # Initialize execution plan in state (will be updated by supervisor_node)
        # Note: We can't modify state here, so we need to do this in a node
        # For now, route to first agent and let the should_continue_sequence handle the rest
        first_agent = agents_to_execute[0]
        return f"{first_agent.value}_agent"


def route_after_agent(state: FinancialAssistantState) -> str:
    """
    Routing function after an agent completes.

    For single-agent scenarios, goes directly to END.
    For multi-agent scenarios, goes to sequence_router to determine next step.

    Args:
        state: Current workflow state

    Returns:
        "sequence_router" or "end"
    """
    execution_plan = state.get("execution_plan")

    # If there's an execution plan, use sequence router
    if execution_plan:
        return "sequence_router"

    # No execution plan = single agent scenario
    return "end"


def route_sequence(state: FinancialAssistantState) -> str:
    """
    Sequence router function - determines next agent or completion.

    This is used by the sequence_router node to decide where to go next.

    Args:
        state: Current workflow state

    Returns:
        Next node name: agent node, "synthesize", or "end"
    """
    execution_plan = state.get("execution_plan")

    if not execution_plan:
        # Shouldn't happen, but fallback to end
        return "end"

    # Check if there are more agents to execute
    agents_queue = execution_plan.get("agents_queue", [])
    current_index = execution_plan.get("current_index", 0)

    if current_index < len(agents_queue):
        # More agents to execute - route to next agent
        next_agent = agents_queue[current_index]
        return f"{next_agent.value}_agent"
    else:
        # All agents executed - go to synthesizer
        return "synthesize"
