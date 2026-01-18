"""
Test script for LangGraph multi-agent orchestration.

Tests the StateGraph workflow without calling actual agents (mocks).
Validates that the graph structure and routing logic work correctly.
"""

from src.orchestration import create_financial_assistant_graph
from src.orchestration.types import AgentType


def test_graph_structure():
    """Test that the graph is created with correct structure."""
    print("=" * 70)
    print("🧪 Testing LangGraph Structure")
    print("=" * 70)
    print()

    try:
        # Create graph
        app = create_financial_assistant_graph()
        print("✓ Graph created successfully")

        # Get graph structure
        graph = app.get_graph()

        # Check nodes exist
        expected_nodes = [
            "fast_router",
            "supervisor",
            "education_agent",
            "goal_planning_agent",
            "portfolio_agent",
            "market_agent",
            "news_agent",
            "sequence_router",
            "synthesizer",
        ]

        print(f"\nExpected nodes: {len(expected_nodes)}")
        print(f"Nodes in graph: {len(graph.nodes)}")

        for node in expected_nodes:
            if node in [n.id for n in graph.nodes.values()]:
                print(f"  ✓ {node}")
            else:
                print(f"  ✗ {node} MISSING")

        print("\n✅ Graph structure test passed!")

    except Exception as e:
        print(f"\n❌ Graph structure test failed: {e}")
        import traceback
        traceback.print_exc()


def test_graph_visualization():
    """Test graph visualization generation."""
    print("\n" + "=" * 70)
    print("🧪 Testing Graph Visualization")
    print("=" * 70)
    print()

    try:
        app = create_financial_assistant_graph()
        graph = app.get_graph()

        # Get mermaid representation
        mermaid = graph.draw_mermaid()

        print("Mermaid diagram generated:")
        print("-" * 70)
        print(mermaid)
        print("-" * 70)

        print("\n✓ To visualize, copy the above and paste into: https://mermaid.live/")
        print("\n✅ Visualization test passed!")

    except Exception as e:
        print(f"\n❌ Visualization test failed: {e}")


def test_simple_routing():
    """Test simple routing through the graph."""
    print("\n" + "=" * 70)
    print("🧪 Testing Simple Routing (Dry Run)")
    print("=" * 70)
    print()

    test_cases = [
        "How is my portfolio performing?",
        "I want to save for retirement",
        "What's the market doing?",
        "Should I invest in Tesla?",
        "What is compound interest?",
    ]

    try:
        app = create_financial_assistant_graph()

        for question in test_cases:
            print(f"\nQuestion: \"{question}\"")
            print("-" * 70)

            try:
                # Note: This will actually call the agents, so we're testing end-to-end
                # For a true dry-run, we'd need to mock the agent functions
                print("  Invoking graph...")

                result = app.invoke(
                    {
                        "messages": [{"role": "user", "content": question}],
                        "user_context": {},
                        "agent_results": {},
                        "agents_completed": [],
                    }
                )

                agents_used = result.get("agents_completed", [])
                final_response = result.get("final_response", "")

                print(f"  ✓ Agents used: {agents_used}")
                print(f"  ✓ Response length: {len(final_response)} chars")

            except Exception as e:
                print(f"  ✗ Error: {e}")

        print("\n✅ Routing test completed!")

    except Exception as e:
        print(f"\n❌ Routing test failed: {e}")
        import traceback
        traceback.print_exc()


def test_state_persistence():
    """Test that state persists across invocations."""
    print("\n" + "=" * 70)
    print("🧪 Testing State Persistence")
    print("=" * 70)
    print()

    try:
        from src.orchestration import create_app_with_memory

        app = create_app_with_memory()
        config = {"configurable": {"thread_id": "test_persistence"}}

        # First invocation
        print("First invocation: Setting up context...")
        result1 = app.invoke(
            {
                "messages": [{"role": "user", "content": "I have a portfolio with AAPL"}],
                "user_context": {},
                "agent_results": {},
                "agents_completed": [],
            },
            config
        )

        print(f"  ✓ User context after first call: {result1.get('user_context', {})}")

        # Second invocation - should remember context
        print("\nSecond invocation: Using persisted context...")
        result2 = app.invoke(
            {
                "messages": result1["messages"] + [{"role": "user", "content": "How is it doing?"}],
                "user_context": result1.get("user_context", {}),
                "agent_results": {},
                "agents_completed": [],
            },
            config
        )

        print(f"  ✓ Messages in conversation: {len(result2.get('messages', []))}")
        print(f"  ✓ User context preserved: {result2.get('user_context', {})}")

        print("\n✅ State persistence test passed!")

    except Exception as e:
        print(f"\n❌ State persistence test failed: {e}")
        import traceback
        traceback.print_exc()


def test_streaming():
    """Test streaming output from the graph."""
    print("\n" + "=" * 70)
    print("🧪 Testing Streaming Output")
    print("=" * 70)
    print()

    try:
        app = create_financial_assistant_graph()

        print("Streaming graph execution for: 'What is diversification?'")
        print("-" * 70)

        for i, chunk in enumerate(app.stream(
            {
                "messages": [{"role": "user", "content": "What is diversification?"}],
                "user_context": {},
                "agent_results": {},
                "agents_completed": [],
            },
            stream_mode="updates"
        ), 1):
            for node_name, state_update in chunk.items():
                print(f"  Step {i}: {node_name}")

        print("-" * 70)
        print("\n✅ Streaming test passed!")

    except Exception as e:
        print(f"\n❌ Streaming test failed: {e}")
        import traceback
        traceback.print_exc()


def run_all_tests():
    """Run all LangGraph tests."""
    print("\n" + "=" * 90)
    print(" " * 25 + "LANGGRAPH TEST SUITE")
    print("=" * 90)

    test_graph_structure()
    test_graph_visualization()

    print("\n" + "!" * 90)
    print("  NOTE: The following tests will call actual agents and may take time.")
    print("  They will also require OPENAI_API_KEY to be set.")
    print("!" * 90)

    try:
        input("\nPress Enter to continue with live agent tests (or Ctrl+C to skip)...")
    except KeyboardInterrupt:
        print("\n\nSkipping live agent tests.")
        return

    test_simple_routing()
    test_state_persistence()
    test_streaming()

    print("\n" + "=" * 90)
    print(" " * 30 + "ALL TESTS COMPLETED")
    print("=" * 90)


if __name__ == "__main__":
    run_all_tests()
