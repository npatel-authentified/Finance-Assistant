"""
AI Finance Assistant - Main Entry Point (LangGraph Version)

Multi-agent system using LangGraph StateGraph for orchestration.
Provides intelligent routing with built-in state management and persistence.

Usage:
    python main_langgraph.py                        # Interactive mode
    python main_langgraph.py "Your question"        # Single question
    uv run python main_langgraph.py "Your question" # With uv
"""

import sys
from typing import Optional

from src.orchestration import create_app_with_memory


# Create app with memory (singleton pattern)
_app = None


def get_app():
    """Get or create the LangGraph app singleton."""
    global _app
    if _app is None:
        _app = create_app_with_memory()
    return _app


def ask_assistant(
    question: str,
    thread_id: str = "default",
    verbose: bool = True
) -> str:
    """
    Ask the assistant a question using LangGraph workflow.

    Args:
        question: User's question
        thread_id: Thread ID for conversation persistence
        verbose: Print workflow progress

    Returns:
        str: Agent response

    Example:
        >>> answer = ask_assistant("How is my portfolio performing?")
    """
    app = get_app()

    config = {"configurable": {"thread_id": thread_id}}

    if verbose:
        print()  # Blank line before workflow execution

    # Stream the workflow execution to show progress
    if verbose:
        for chunk in app.stream(
            {
                "messages": [{"role": "user", "content": question}],
                "user_context": {},
                "agent_results": {},
                "agents_completed": [],
            },
            config,
            stream_mode="updates",  # Show updates for each node
        ):
            # chunk is a dict with node name as key
            for node_name, state_update in chunk.items():
                # Show node execution
                if node_name == "fast_router":
                    router_decision = state_update.get("router_decision")
                    if router_decision:
                        print(f"🔍 Fast Router: {router_decision.reasoning}")
                        print(f"   Confidence: {router_decision.confidence:.2f}")
                        if router_decision.route == "direct":
                            print(f"   → Direct route to: {router_decision.agent.value}\n")
                        else:
                            print(f"   → Using supervisor (low confidence)\n")

                elif node_name == "supervisor":
                    supervisor_decision = state_update.get("supervisor_decision")
                    if supervisor_decision:
                        print(f"🎯 Supervisor Decision: {supervisor_decision.reasoning}")
                        print(f"   Primary: {supervisor_decision.primary_agent.value}")
                        if supervisor_decision.secondary_agents:
                            secondary = [a.value for a in supervisor_decision.secondary_agents]
                            print(f"   Secondary: {secondary}")
                            print(f"   Mode: {supervisor_decision.execution_mode}")
                        print()

                elif node_name.endswith("_agent"):
                    agent_name = node_name.replace("_agent", "")
                    print(f"▶  Executing {agent_name} agent...")

                elif node_name == "sequence_router":
                    print(f"➡️  Routing to next agent...")

                elif node_name == "synthesizer":
                    print(f"📋 Synthesizing results...\n")

        # Get final result
        final_state = app.get_state(config)
        response = final_state.values.get("final_response", "No response generated")

    else:
        # Non-verbose mode - just get the result
        result = app.invoke(
            {
                "messages": [{"role": "user", "content": question}],
                "user_context": {},
                "agent_results": {},
                "agents_completed": [],
            },
            config
        )
        response = result.get("final_response", "No response generated")

    return response


def interactive_mode(thread_id: str = "interactive"):
    """
    Interactive CLI mode with LangGraph state persistence.

    Maintains full conversation context using LangGraph checkpointing.

    Args:
        thread_id: Thread ID for this conversation session
    """
    print("=" * 70)
    print("🤖 AI Finance Assistant (LangGraph Version)")
    print("=" * 70)
    print()
    print("Powered by LangGraph StateGraph with intelligent multi-agent routing.")
    print()
    print("Commands:")
    print("  /help      - Show available agents")
    print("  /state     - Show current conversation state")
    print("  /clear     - Clear conversation history (new thread)")
    print("  /graph     - Visualize workflow graph")
    print("  /exit      - Exit the assistant")
    print()
    print("=" * 70)
    print()

    current_thread = thread_id

    while True:
        try:
            question = input("You: ").strip()

            if not question:
                continue

            # Handle commands
            if question.lower() in ["/exit", "/quit", "exit", "quit"]:
                print("\n👋 Goodbye! Thanks for using AI Finance Assistant.\n")
                break

            elif question.lower() == "/help":
                print("\n📚 Available Specialized Agents:")
                print("  • education       - Financial concepts, taxes, definitions (RAG)")
                print("  • goal_planning   - Financial goal setting and tracking")
                print("  • portfolio       - Portfolio analysis (for current investors)")
                print("  • market          - Market data and stock analysis")
                print("  • news            - Investment research (for potential investors)")
                print()
                print("The system automatically routes your question to the right agent(s)!")
                print()
                continue

            elif question.lower() == "/state":
                app = get_app()
                config = {"configurable": {"thread_id": current_thread}}
                state = app.get_state(config)

                print("\n📊 Current Conversation State:")
                print(f"  Thread ID: {current_thread}")
                print(f"  Messages: {len(state.values.get('messages', []))} messages")
                print(f"  User Context: {state.values.get('user_context', {})}")
                print(f"  Current Agent: {state.values.get('current_agent', 'None')}")
                print(f"  Agents Completed: {state.values.get('agents_completed', [])}")
                print()
                continue

            elif question.lower() == "/clear":
                # Start a new thread
                import uuid
                current_thread = f"interactive_{uuid.uuid4().hex[:8]}"
                print(f"\n🗑️  Started new conversation (Thread: {current_thread})\n")
                continue

            elif question.lower() == "/graph":
                print("\n📊 Generating graph visualization...")
                from src.orchestration import visualize_graph
                visualize_graph()
                print()
                continue

            # Process question
            answer = ask_assistant(question, current_thread, verbose=True)
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using AI Finance Assistant.\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()
            continue


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Single question mode
        question = " ".join(sys.argv[1:])

        print("=" * 70)
        print("🤖 AI Finance Assistant (LangGraph)")
        print("=" * 70)

        answer = ask_assistant(question, thread_id="cli", verbose=True)
        print()

    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
