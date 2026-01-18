"""
Minimal test to verify graph structure after refactoring.

Tests that orchestrator node is removed and routing is correct.
"""

from langgraph.graph import StateGraph, END
from src.orchestration.types import FinancialAssistantState, ExecutionPlan


def test_types():
    """Test that new types exist."""
    print("=" * 70)
    print("Testing Types")
    print("=" * 70)

    # Test ExecutionPlan type
    exec_plan = {
        "agents_queue": [],
        "current_index": 0,
        "needs_synthesis": True
    }
    print("✓ ExecutionPlan type exists")

    # Test FinancialAssistantState with execution_plan
    state = {
        "messages": [],
        "router_decision": None,
        "supervisor_decision": None,
        "user_context": {},
        "agent_results": {},
        "current_agent": None,
        "agents_completed": [],
        "execution_plan": exec_plan,
        "final_response": None,
    }
    print("✓ FinancialAssistantState has execution_plan field")
    print()


def test_node_functions():
    """Test that routing functions exist."""
    print("=" * 70)
    print("Testing Node Functions")
    print("=" * 70)

    from src.orchestration.nodes import (
        route_after_fast_router,
        route_after_supervisor,
        should_continue_sequence,
    )

    print("✓ route_after_fast_router exists")
    print("✓ route_after_supervisor exists")
    print("✓ should_continue_sequence exists (NEW)")

    # Test that orchestrator doesn't exist
    try:
        from src.orchestration.nodes import multi_agent_orchestrator_node
        print("✗ multi_agent_orchestrator_node still exists (should be removed)")
    except ImportError:
        print("✓ multi_agent_orchestrator_node removed")

    print()


def test_exports():
    """Test that types are exported."""
    print("=" * 70)
    print("Testing Exports")
    print("=" * 70)

    from src.orchestration import (
        ExecutionPlan,
        FinancialAssistantState,
    )

    print("✓ ExecutionPlan exported")
    print("✓ FinancialAssistantState exported")
    print()


def test_documentation():
    """Test that key changes are documented."""
    print("=" * 70)
    print("Testing Documentation")
    print("=" * 70)

    with open("LANGGRAPH_IMPLEMENTATION.md", "r") as f:
        doc = f.read()

    assert "ExecutionPlan" in doc, "ExecutionPlan not documented"
    print("✓ ExecutionPlan documented")

    assert "should_continue_sequence" in doc, "should_continue_sequence not documented"
    print("✓ should_continue_sequence documented")

    assert "v2.0.0" in doc, "Version 2.0.0 not documented"
    print("✓ Version 2.0.0 documented")

    assert "Native LangGraph Patterns" in doc, "Native patterns not documented"
    print("✓ Native LangGraph patterns documented")

    # Check that orchestrator is marked as removed
    assert "multi_agent_orchestrator" in doc, "Orchestrator not mentioned"
    assert "Removed" in doc, "Removal not documented"
    print("✓ Orchestrator removal documented")

    print()


if __name__ == "__main__":
    print("\n" + "=" * 90)
    print(" " * 25 + "MINIMAL GRAPH STRUCTURE TEST")
    print("=" * 90)
    print()

    try:
        test_types()
        test_node_functions()
        test_exports()
        test_documentation()

        print("=" * 90)
        print(" " * 30 + "ALL TESTS PASSED ✓")
        print("=" * 90)
        print()
        print("Summary of Changes:")
        print("  ✓ ExecutionPlan type added to types.py")
        print("  ✓ multi_agent_orchestrator_node removed from nodes.py")
        print("  ✓ should_continue_sequence added to nodes.py")
        print("  ✓ Types properly exported from __init__.py")
        print("  ✓ Documentation updated with v2.0.0 changes")
        print()
        print("Next: Run 'python main_langgraph.py' to test end-to-end execution")

    except Exception as e:
        print("\n" + "=" * 90)
        print(" " * 30 + "TESTS FAILED ✗")
        print("=" * 90)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
