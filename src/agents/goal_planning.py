"""
Financial Goal Planning Agent

This agent helps users create, manage, and achieve their financial goals through
conversational guidance, analysis tools, and educational content.
"""

import sys
from pathlib import Path

# Add project root to Python path for direct execution
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.core.tools.goal_planning import (
    create_goal,
    calculate_savings_required,
    prioritize_goals,
    analyze_goal_tradeoffs,
    check_goal_feasibility,
    list_goals,
    update_goal_progress,
    delete_goal,
    get_goal_categories,
)
from src.rag.retrieval_and_generation import retrieve_tool
from src.config import get_openai_api_key, DEFAULT_LLM_MODEL, ConfigError
from src.prompts import GOAL_PLANNER_PROMPT


def create_goal_planning_assistant():
    """
    Create a financial goal planning assistant agent.

    Returns:
        Agent: Configured LangGraph agent with goal planning and RAG capabilities

    Raises:
        ConfigError: If OPENAI_API_KEY is not set
    """
    # Get OpenAI API key from centralized config
    openai_api_key = get_openai_api_key()

    # Initialize LLM
    llm = ChatOpenAI(
        model=DEFAULT_LLM_MODEL,
        temperature=0.3,  # Slightly higher for conversational tone
        openai_api_key=openai_api_key
    )

    # Collect all tools
    tools = [
        # Goal management tools
        create_goal,
        list_goals,
        update_goal_progress,
        delete_goal,
        get_goal_categories,
        # Analysis tools
        calculate_savings_required,
        check_goal_feasibility,
        prioritize_goals,
        analyze_goal_tradeoffs,
        # Educational tool
        retrieve_tool,
    ]

    # Create agent with tools
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=GOAL_PLANNER_PROMPT
    )

    return agent


def ask_question(messages, verbose: bool = True):
    """
    Ask the goal planning agent a question and get an answer with conversation context.

    Args:
        messages: Either a string (backward compatibility) or list of message dicts
                  [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        verbose: If True, print streaming responses

    Returns:
        str: The agent's response
    """
    # Handle backward compatibility: convert string to message list
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    try:
        agent = create_goal_planning_assistant()

        # Extract last question for display
        last_question = messages[-1]["content"] if messages else ""

        if verbose:
            print(f"\nYou: {last_question}\n")
            print("Goal Planner: ", end="", flush=True)

        response_text = ""

        # Stream the agent's response with full conversation context
        for event in agent.stream(
            {"messages": messages},  # Pass full context
            stream_mode="values",
        ):
            if "messages" in event and len(event["messages"]) > 0:
                last_message = event["messages"][-1]

                if verbose:
                    last_message.pretty_print()

                # Collect the response
                if hasattr(last_message, 'content'):
                    response_text = last_message.content

        return response_text

    except ConfigError as e:
        error_msg = f"Configuration Error: {str(e)}"
        if verbose:
            print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        if verbose:
            print(error_msg)
        return error_msg


def interactive_session():
    """
    Run an interactive goal planning session with the user.
    """
    print("=" * 70)
    print("🎯 Financial Goal Planning Assistant")
    print("=" * 70)
    print("\nWelcome! I'm here to help you plan and achieve your financial goals.")
    print("You can:")
    print("  • Create new financial goals")
    print("  • Calculate how much you need to save")
    print("  • Prioritize multiple goals")
    print("  • Analyze trade-offs between goals")
    print("  • Learn about financial planning strategies")
    print("\nType 'exit' or 'quit' to end the session.")
    print("=" * 70)

    agent = create_goal_planning_assistant()

    # Conversation history
    messages = []

    while True:
        # Get user input
        user_input = input("\n💬 You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\n👋 Thanks for using the Goal Planning Assistant! Good luck with your goals!")
            break

        # Add user message
        messages.append({"role": "user", "content": user_input})

        print("\n🎯 Goal Planner: ", end="", flush=True)

        response_text = ""

        # Stream the agent's response
        try:
            for event in agent.stream(
                {"messages": messages},
                stream_mode="values",
            ):
                if "messages" in event and len(event["messages"]) > 0:
                    last_message = event["messages"][-1]
                    last_message.pretty_print()

                    # Collect the response
                    if hasattr(last_message, 'content'):
                        response_text = last_message.content

            # Add assistant message to history
            if response_text:
                messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Let's try again...")


# Example usage
if __name__ == "__main__":
    """
    Example demonstrating the Goal Planning Agent.

    Make sure to:
    1. Set up the vector database first (run ingestion.py) for educational content
    2. Set OPENAI_API_KEY and PINECONE_API_KEY environment variables
    """
    import sys

    # Sample questions
    sample_questions = [
        "I want to start planning my financial goals. Can you help?",
        "I want to save for an emergency fund of $10,000 in 12 months",
        "I also want to save for a vacation that costs $5,000 in 6 months",
    ]

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
            # Run interactive session
            interactive_session()
        else:
            # Use command line argument as question
            question = " ".join(sys.argv[1:])
            ask_question(question)
    else:
        # Show examples
        print("=" * 70)
        print("Financial Goal Planning Agent - Example Usage")
        print("=" * 70)

        for i, question in enumerate(sample_questions, 1):
            print(f"\n{'='*70}")
            print(f"Example {i}/{len(sample_questions)}")
            print(f"{'='*70}")

            ask_question(question)

            if i < len(sample_questions):
                input("\nPress Enter to continue to next question...")

        print("\n" + "=" * 70)
        print("Example Complete!")
        print("=" * 70)
        print("\nTo ask your own question, run:")
        print("  python -m src.agents.goal_planning 'Your question here'")
        print("\nOr run an interactive session:")
        print("  python -m src.agents.goal_planning --interactive")
