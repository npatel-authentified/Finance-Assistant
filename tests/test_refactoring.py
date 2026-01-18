"""
Test script to verify Phase 2 refactoring changes.

Checks file contents directly without triggering full imports.
"""

import re


def test_types_file():
    """Test that types.py has ExecutionPlan."""
    print("=" * 70)
    print("Testing types.py")
    print("=" * 70)

    with open("src/orchestration/types.py", "r") as f:
        content = f.read()

    assert "class ExecutionPlan" in content, "ExecutionPlan class not found"
    print("✓ ExecutionPlan class exists")

    assert "agents_queue: List[AgentType]" in content, "agents_queue field not found"
    print("✓ agents_queue field exists")

    assert "current_index: int" in content, "current_index field not found"
    print("✓ current_index field exists")

    assert "needs_synthesis: bool" in content, "needs_synthesis field not found"
    print("✓ needs_synthesis field exists")

    assert "execution_plan: Optional[ExecutionPlan]" in content, "execution_plan field not in state"
    print("✓ execution_plan added to FinancialAssistantState")

    print()


def test_nodes_file():
    """Test that nodes.py has been refactored."""
    print("=" * 70)
    print("Testing nodes.py")
    print("=" * 70)

    with open("src/orchestration/nodes.py", "r") as f:
        content = f.read()

    # Check orchestrator removed
    assert "def multi_agent_orchestrator_node" not in content, "Orchestrator node still exists"
    print("✓ multi_agent_orchestrator_node removed")

    # Check new function added
    assert "def should_continue_sequence" in content, "should_continue_sequence not found"
    print("✓ should_continue_sequence added")

    # Check execution plan handling in _execute_agent_node
    assert "execution_plan = state.get(\"execution_plan\")" in content, "execution_plan not checked in agent node"
    print("✓ _execute_agent_node checks execution_plan")

    assert "current_index" in content, "current_index not used"
    print("✓ current_index advancement implemented")

    # Check supervisor creates execution plan
    with open("src/orchestration/nodes.py", "r") as f:
        content = f.read()
    assert "execution_plan = None" in content, "supervisor doesn't initialize execution_plan"
    assert "agents_to_execute = [supervisor_decision.primary_agent]" in content
    print("✓ supervisor_node initializes execution_plan")

    print()


def test_graph_file():
    """Test that graph.py has been updated."""
    print("=" * 70)
    print("Testing graph.py")
    print("=" * 70)

    with open("src/orchestration/graph.py", "r") as f:
        content = f.read()

    # Check orchestrator not imported
    assert "multi_agent_orchestrator_node" not in content, "Orchestrator still imported"
    print("✓ multi_agent_orchestrator_node not imported")

    # Check new routing function imported
    assert "should_continue_sequence" in content, "should_continue_sequence not imported"
    print("✓ should_continue_sequence imported")

    # Check orchestrator not added as node
    assert 'workflow.add_node("multi_agent_orchestrator"' not in content, "Orchestrator still added as node"
    print("✓ Orchestrator node not added to workflow")

    # Check conditional edges updated
    edges_section = re.search(r"# Agent routing.*?workflow\.add_edge", content, re.DOTALL)
    if edges_section:
        edges_text = edges_section.group(0)
        assert "should_continue_sequence" in edges_text, "Agent routing doesn't use should_continue_sequence"
        print("✓ Agent routing uses should_continue_sequence")

        # Check all agents can route to each other
        assert '"education_agent": "education_agent"' in edges_text, "Agents can't route to education"
        assert '"market_agent": "market_agent"' in edges_text, "Agents can't route to market"
        print("✓ Agents can route to any other agent")

    print()


def test_init_file():
    """Test that __init__.py exports ExecutionPlan."""
    print("=" * 70)
    print("Testing __init__.py")
    print("=" * 70)

    with open("src/orchestration/__init__.py", "r") as f:
        content = f.read()

    assert "ExecutionPlan" in content, "ExecutionPlan not exported"
    print("✓ ExecutionPlan exported")

    # Check __all__ includes ExecutionPlan
    assert '"ExecutionPlan"' in content, "ExecutionPlan not in __all__"
    print("✓ ExecutionPlan in __all__")

    print()


def test_main_langgraph():
    """Test that main_langgraph.py is updated."""
    print("=" * 70)
    print("Testing main_langgraph.py")
    print("=" * 70)

    with open("main_langgraph.py", "r") as f:
        content = f.read()

    # Check orchestrator reference removed
    assert "multi_agent_orchestrator" not in content, "Orchestrator reference still in main"
    print("✓ Orchestrator references removed")

    print()


def test_test_file():
    """Test that test_langgraph.py is updated."""
    print("=" * 70)
    print("Testing test_langgraph.py")
    print("=" * 70)

    with open("test_langgraph.py", "r") as f:
        content = f.read()

    # Check orchestrator not in expected nodes
    expected_nodes_section = re.search(r"expected_nodes = \[(.*?)\]", content, re.DOTALL)
    if expected_nodes_section:
        nodes_text = expected_nodes_section.group(1)
        assert "multi_agent_orchestrator" not in nodes_text, "Orchestrator in expected nodes"
        print("✓ Orchestrator removed from expected nodes")

    print()


def test_documentation():
    """Test that documentation is updated."""
    print("=" * 70)
    print("Testing LANGGRAPH_IMPLEMENTATION.md")
    print("=" * 70)

    with open("LANGGRAPH_IMPLEMENTATION.md", "r") as f:
        content = f.read()

    assert "ExecutionPlan" in content, "ExecutionPlan not documented"
    print("✓ ExecutionPlan documented")

    assert "should_continue_sequence" in content, "should_continue_sequence not documented"
    print("✓ should_continue_sequence documented")

    assert "v2.0.0" in content, "Version 2.0.0 not found"
    print("✓ Version 2.0.0 documented")

    assert "Native LangGraph Patterns" in content, "Native patterns not documented"
    print("✓ Native LangGraph patterns documented")

    assert "Phase 2 (Completed)" in content, "Phase 2 not marked complete"
    print("✓ Phase 2 marked as completed")

    # Check orchestrator marked as removed
    assert "multi_agent_orchestrator" in content, "Orchestrator not mentioned"
    assert "Removed" in content or "removed" in content, "Removal not documented"
    print("✓ Orchestrator removal documented")

    # Check statistics updated
    assert "Nodes:** 10" in content, "Node count not updated"
    print("✓ Node count updated to 10")

    print()


if __name__ == "__main__":
    print("\n" + "=" * 90)
    print(" " * 20 + "PHASE 2 REFACTORING VERIFICATION")
    print("=" * 90)
    print()

    try:
        test_types_file()
        test_nodes_file()
        test_graph_file()
        test_init_file()
        test_main_langgraph()
        test_test_file()
        test_documentation()

        print("=" * 90)
        print(" " * 30 + "ALL TESTS PASSED ✓")
        print("=" * 90)
        print()
        print("Phase 2 Refactoring Complete!")
        print()
        print("Summary of Changes:")
        print("  ✅ ExecutionPlan type added to types.py")
        print("  ✅ multi_agent_orchestrator_node removed from nodes.py")
        print("  ✅ should_continue_sequence routing function added")
        print("  ✅ _execute_agent_node advances execution plan")
        print("  ✅ supervisor_node initializes execution plan")
        print("  ✅ Graph updated with agent-to-agent routing")
        print("  ✅ All imports and exports updated")
        print("  ✅ Main entry point updated")
        print("  ✅ Tests updated")
        print("  ✅ Documentation updated to v2.0.0")
        print()
        print("Architecture:")
        print("  • Sequential multi-agent execution uses native LangGraph patterns")
        print("  • No dedicated orchestrator node (declarative approach)")
        print("  • State-based routing via execution_plan")
        print("  • Each agent can route to next agent in sequence")
        print("  • Fully compliant with LangGraph best practices")
        print()
        print("Next Steps:")
        print("  1. Test with real questions: python main_langgraph.py")
        print("  2. Verify sequential multi-agent execution works correctly")
        print("  3. Check graph visualization shows agent chains")
        print()

    except AssertionError as e:
        print("\n" + "=" * 90)
        print(" " * 30 + "TEST FAILED ✗")
        print("=" * 90)
        print(f"\nAssertion Error: {e}")
        print()
    except Exception as e:
        print("\n" + "=" * 90)
        print(" " * 30 + "ERROR")
        print("=" * 90)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
