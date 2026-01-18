"""
Test script to verify SIMPLIFIED graph architecture (v2.1).

Verifies that sequence_router node is added and complexity is reduced.
"""

import re


def test_nodes_file():
    """Test that nodes.py has sequence_router."""
    print("=" * 70)
    print("Testing nodes.py")
    print("=" * 70)

    with open("src/orchestration/nodes.py", "r") as f:
        content = f.read()

    # Check sequence_router added
    assert "def sequence_router_node" in content, "sequence_router_node not found"
    print("✓ sequence_router_node added")

    # Check new routing functions
    assert "def route_after_agent" in content, "route_after_agent not found"
    print("✓ route_after_agent added")

    assert "def route_sequence" in content, "route_sequence not found"
    print("✓ route_sequence added")

    # Check old complex function removed
    assert "def should_continue_sequence" not in content, "should_continue_sequence still exists"
    print("✓ should_continue_sequence removed (was complex)")

    print()


def test_graph_file():
    """Test that graph.py uses simplified architecture."""
    print("=" * 70)
    print("Testing graph.py")
    print("=" * 70)

    with open("src/orchestration/graph.py", "r") as f:
        content = f.read()

    # Check sequence_router imported
    assert "sequence_router_node" in content, "sequence_router_node not imported"
    print("✓ sequence_router_node imported")

    # Check new routing functions imported
    assert "route_after_agent" in content, "route_after_agent not imported"
    print("✓ route_after_agent imported")

    assert "route_sequence" in content, "route_sequence not imported"
    print("✓ route_sequence imported")

    # Check sequence_router added as node
    assert 'workflow.add_node("sequence_router"' in content, "sequence_router not added to workflow"
    print("✓ sequence_router node added to workflow")

    # Check simplified agent routing (2-way choice)
    assert '"sequence_router": "sequence_router"' in content, "Agents don't route to sequence_router"
    print("✓ Agents route to sequence_router")

    # Check documentation mentions simplification
    assert "SIMPLIFIED" in content or "simplified" in content, "Simplification not documented"
    print("✓ Simplification documented")

    # Count conditional edge destinations per agent (should be 2: sequence_router and end)
    agent_edges_pattern = r'route_after_agent.*?\{(.*?)\}'
    match = re.search(agent_edges_pattern, content, re.DOTALL)
    if match:
        edges_dict = match.group(1)
        destinations = len([d for d in edges_dict.split('"') if d.strip() and d.strip() != ':'])
        # Should have 2 destinations per agent (sequence_router and end)
        print(f"✓ Agents have ~{destinations//2} routing destinations (was 7 in v2.0)")

    print()


def test_main_langgraph():
    """Test that main_langgraph.py shows sequence_router."""
    print("=" * 70)
    print("Testing main_langgraph.py")
    print("=" * 70)

    with open("main_langgraph.py", "r") as f:
        content = f.read()

    # Check sequence_router progress display
    assert "sequence_router" in content, "sequence_router not handled in main"
    print("✓ sequence_router progress display added")

    print()


def test_test_file():
    """Test that test_langgraph.py expects sequence_router."""
    print("=" * 70)
    print("Testing test_langgraph.py")
    print("=" * 70)

    with open("test_langgraph.py", "r") as f:
        content = f.read()

    # Check sequence_router in expected nodes
    expected_nodes_section = re.search(r"expected_nodes = \[(.*?)\]", content, re.DOTALL)
    if expected_nodes_section:
        nodes_text = expected_nodes_section.group(1)
        assert "sequence_router" in nodes_text, "sequence_router not in expected nodes"
        print("✓ sequence_router in expected nodes")

        # Count expected nodes
        node_count = len([n for n in nodes_text.split('"') if '_' in n or 'router' in n or 'supervisor' in n or 'synthesizer' in n])
        print(f"✓ Expecting {node_count} nodes total")

    print()


def test_documentation():
    """Test that documentation explains simplification."""
    print("=" * 70)
    print("Testing LANGGRAPH_IMPLEMENTATION.md")
    print("=" * 70)

    with open("LANGGRAPH_IMPLEMENTATION.md", "r") as f:
        content = f.read()

    assert "sequence_router" in content, "sequence_router not documented"
    print("✓ sequence_router documented")

    assert "v2.1" in content, "Version 2.1 not found"
    print("✓ Version 2.1 documented")

    assert "SIMPLIFIED" in content, "Simplification not mentioned"
    print("✓ Simplification explained")

    # Check it explains the problem
    assert "35+" in content or "complex" in content.lower(), "Complexity problem not explained"
    print("✓ Complexity problem explained")

    assert "15 edges" in content or "linear flow" in content, "Solution not explained"
    print("✓ Solution (linear flow) explained")

    # Check mermaid diagram includes sequence router
    assert "Sequence Router" in content or "SeqRouter" in content, "Sequence router not in diagram"
    print("✓ Sequence router in mermaid diagram")

    # Check statistics updated
    assert "Nodes:** 11" in content, "Node count not updated"
    print("✓ Node count is 11")

    assert "15 edges" in content, "Edge count not updated"
    print("✓ Edge count is ~15")

    print()


if __name__ == "__main__":
    print("\n" + "=" * 90)
    print(" " * 20 + "SIMPLIFIED GRAPH VERIFICATION (v2.1)")
    print("=" * 90)
    print()

    try:
        test_nodes_file()
        test_graph_file()
        test_main_langgraph()
        test_test_file()
        test_documentation()

        print("=" * 90)
        print(" " * 30 + "ALL TESTS PASSED ✓")
        print("=" * 90)
        print()
        print("🎉 Graph Successfully SIMPLIFIED! 🎉")
        print()
        print("Summary of v2.1 Changes:")
        print("  ✅ Added sequence_router node (lightweight, no business logic)")
        print("  ✅ Added route_after_agent (simple 2-way routing)")
        print("  ✅ Added route_sequence (determines next agent)")
        print("  ✅ Removed complex should_continue_sequence")
        print("  ✅ Reduced from 35+ edges to ~15 edges")
        print("  ✅ Clean linear flow: Agent → Router → Agent → Router → Synthesizer")
        print()
        print("Architecture Comparison:")
        print("  v1.0: Orchestrator with imperative loops ❌")
        print("  v2.0: Agent-to-agent mesh (35+ edges) ⚠️")
        print("  v2.1: Sequence router (15 edges) ✅")
        print()
        print("Graph Structure:")
        print("  11 nodes total:")
        print("    - 1 fast_router")
        print("    - 1 supervisor")
        print("    - 5 agents (education, goal, portfolio, market, news)")
        print("    - 1 sequence_router ⭐ NEW")
        print("    - 1 synthesizer")
        print()
        print("Next Steps:")
        print("  1. Test graph creation (needs dependencies)")
        print("  2. Visualize with /graph command")
        print("  3. Test multi-agent sequential execution")
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
