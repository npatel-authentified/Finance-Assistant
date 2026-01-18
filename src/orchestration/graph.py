"""
LangGraph StateGraph Workflow

Assembles all nodes into a complete multi-agent orchestration workflow.
Uses StateGraph for declarative workflow definition with built-in state management.
"""

from typing import Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .types import FinancialAssistantState
from .nodes import (
    fast_router_node,
    supervisor_node,
    education_agent_node,
    goal_planning_agent_node,
    portfolio_agent_node,
    market_agent_node,
    news_agent_node,
    sequence_router_node,
    synthesizer_node,
    route_after_fast_router,
    route_after_supervisor,
    route_after_agent,
    route_sequence,
)


def create_financial_assistant_graph(
    checkpointer: Optional[MemorySaver] = None
):
    """
    Create the financial assistant LangGraph workflow with SIMPLIFIED architecture.

    This creates a clean, linear StateGraph with:
    - Fast router for quick pattern-based routing
    - Supervisor for LLM-based intelligent routing (creates execution plan)
    - 5 specialized agent nodes
    - Sequence router (lightweight routing node - no business logic)
    - Synthesizer for combining multi-agent results

    Graph flow:
    - Single agent: Supervisor → Agent → END
    - Multi-agent: Supervisor → Agent1 → Sequence Router → Agent2 → Sequence Router → Synthesizer

    This is MUCH simpler than having every agent route to every other agent (35+ edges).
    Now: ~15 edges in a clean linear flow.

    Args:
        checkpointer: Optional checkpointer for state persistence
                     (e.g., MemorySaver for in-memory, SqliteSaver for persistence)

    Returns:
        Compiled LangGraph application

    Example:
        >>> from langgraph.checkpoint.memory import MemorySaver
        >>>
        >>> memory = MemorySaver()
        >>> app = create_financial_assistant_graph(checkpointer=memory)
        >>>
        >>> # Run with session persistence
        >>> config = {"configurable": {"thread_id": "user_123"}}
        >>> result = app.invoke(
        ...     {"messages": [{"role": "user", "content": "How is my portfolio?"}]},
        ...     config
        ... )
    """
    # Create workflow
    workflow = StateGraph(FinancialAssistantState)

    # Add all nodes
    workflow.add_node("fast_router", fast_router_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("education_agent", education_agent_node)
    workflow.add_node("goal_planning_agent", goal_planning_agent_node)
    workflow.add_node("portfolio_agent", portfolio_agent_node)
    workflow.add_node("market_agent", market_agent_node)
    workflow.add_node("news_agent", news_agent_node)
    workflow.add_node("sequence_router", sequence_router_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # Set entry point
    workflow.set_entry_point("fast_router")

    # Conditional routing from fast router
    # Routes to either supervisor or directly to an agent
    workflow.add_conditional_edges(
        "fast_router",
        route_after_fast_router,
        {
            "supervisor": "supervisor",
            "education_agent": "education_agent",
            "goal_planning_agent": "goal_planning_agent",
            "portfolio_agent": "portfolio_agent",
            "market_agent": "market_agent",
            "news_agent": "news_agent",
        }
    )

    # Conditional routing from supervisor
    # Routes to single agent (first agent in execution plan for multi-agent)
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "education_agent": "education_agent",
            "goal_planning_agent": "goal_planning_agent",
            "portfolio_agent": "portfolio_agent",
            "market_agent": "market_agent",
            "news_agent": "news_agent",
        }
    )

    # Agent routing - simple 2-way choice: sequence_router (multi-agent) or END (single-agent)
    for agent_node in [
        "education_agent",
        "goal_planning_agent",
        "portfolio_agent",
        "market_agent",
        "news_agent"
    ]:
        workflow.add_conditional_edges(
            agent_node,
            route_after_agent,
            {
                "sequence_router": "sequence_router",
                "end": END,
            }
        )

    # Sequence router decides: next agent or synthesizer
    workflow.add_conditional_edges(
        "sequence_router",
        route_sequence,
        {
            "education_agent": "education_agent",
            "goal_planning_agent": "goal_planning_agent",
            "portfolio_agent": "portfolio_agent",
            "market_agent": "market_agent",
            "news_agent": "news_agent",
            "synthesize": "synthesizer",
        }
    )

    # Synthesizer is the final step
    workflow.add_edge("synthesizer", END)

    # Compile the graph
    if checkpointer:
        app = workflow.compile(checkpointer=checkpointer)
    else:
        app = workflow.compile()

    return app


def create_app_with_memory():
    """
    Create financial assistant app with in-memory state persistence.

    Useful for maintaining conversation context across multiple invocations
    within the same session.

    Returns:
        Compiled LangGraph application with MemorySaver

    Example:
        >>> app = create_app_with_memory()
        >>>
        >>> config = {"configurable": {"thread_id": "user_123"}}
        >>>
        >>> # First question
        >>> result1 = app.invoke(
        ...     {"messages": [{"role": "user", "content": "I have a portfolio"}]},
        ...     config
        ... )
        >>>
        >>> # Second question - remembers previous context
        >>> result2 = app.invoke(
        ...     {"messages": [{"role": "user", "content": "How is it performing?"}]},
        ...     config
        ... )
    """
    memory = MemorySaver()
    return create_financial_assistant_graph(checkpointer=memory)


def visualize_graph(output_file: str = "financial_assistant_graph.png"):
    """
    Visualize the graph structure.

    Requires graphviz to be installed:
        pip install pygraphviz

    Args:
        output_file: Output file path for the graph image

    Example:
        >>> visualize_graph("my_graph.png")
    """
    try:
        app = create_financial_assistant_graph()

        # Get mermaid syntax
        mermaid = app.get_graph().draw_mermaid()

        print("Graph structure (Mermaid syntax):")
        print(mermaid)
        print(f"\nTo visualize, paste the above into: https://mermaid.live/")

        # Try to save PNG if graphviz is available
        try:
            png_data = app.get_graph().draw_mermaid_png()
            with open(output_file, "wb") as f:
                f.write(png_data)
            print(f"\nGraph saved to: {output_file}")
        except Exception as e:
            print(f"\nCouldn't save PNG (graphviz not installed): {e}")

    except Exception as e:
        print(f"Error visualizing graph: {e}")


# Example usage and helper functions

def invoke_with_question(question: str, thread_id: str = "default") -> str:
    """
    Simple helper to invoke the graph with a question.

    Args:
        question: User's question
        thread_id: Thread ID for conversation persistence

    Returns:
        Agent's response

    Example:
        >>> response = invoke_with_question("How is my portfolio?")
        >>> print(response)
    """
    app = create_app_with_memory()

    config = {"configurable": {"thread_id": thread_id}}

    result = app.invoke(
        {
            "messages": [{"role": "user", "content": question}],
            "user_context": {},
            "agent_results": {},
            "agents_completed": [],
        },
        config
    )

    return result.get("final_response", "No response generated")


def stream_with_question(question: str, thread_id: str = "default"):
    """
    Stream the graph execution with a question.

    Shows intermediate results as each node executes.

    Args:
        question: User's question
        thread_id: Thread ID for conversation persistence

    Yields:
        Dict with node name and updated state

    Example:
        >>> for chunk in stream_with_question("What's the market doing?"):
        ...     print(f"Node: {chunk['node']}")
        ...     print(f"State: {chunk['state']}")
    """
    app = create_app_with_memory()

    config = {"configurable": {"thread_id": thread_id}}

    for chunk in app.stream(
        {
            "messages": [{"role": "user", "content": question}],
            "user_context": {},
            "agent_results": {},
            "agents_completed": [],
        },
        config
    ):
        yield chunk


if __name__ == "__main__":
    """
    Test the graph creation and visualization.
    """
    print("Creating Financial Assistant LangGraph...")
    print("=" * 70)

    # Create app
    app = create_financial_assistant_graph()
    print("✓ Graph created successfully")

    # Try to visualize
    print("\nGenerating graph visualization...")
    visualize_graph()

    print("\n" + "=" * 70)
    print("Graph Structure:")
    print("=" * 70)
    print("""
    START
      ↓
    Fast Router (pattern/keyword matching)
      ↓
    ├─ High Confidence → Direct to Agent → END
    │
    └─ Low Confidence → Supervisor (LLM, creates execution plan)
         ↓
       ├─ Single Agent → Agent → END
       │
       └─ Multi-Agent → Agent1 → Agent2 → ... → Synthesizer → END
                        (sequential via conditional routing)
    """)

    print("\nTo test the graph:")
    print("  python -m src.orchestration.graph")
    print("\nOr import and use:")
    print("  from src.orchestration.graph import create_app_with_memory")
    print("  app = create_app_with_memory()")
    print("  result = app.invoke({...})")
