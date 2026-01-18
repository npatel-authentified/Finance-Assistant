"""
Portfolio Analysis Agent

This agent helps users analyze their investment portfolios with comprehensive tools for
diversification analysis, risk assessment, performance tracking, and rebalancing recommendations.
"""

import sys
from pathlib import Path

# Add project root to Python path for direct execution
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.core.tools.portfolio_analysis import (
    get_portfolio_summary,
    analyze_portfolio_diversification,
    calculate_portfolio_performance,
    analyze_portfolio_risk,
    compare_portfolio_to_benchmark,
    get_rebalancing_recommendations,
    analyze_individual_position,
)
from src.config import get_openai_api_key, DEFAULT_LLM_MODEL, ConfigError
from src.prompts import PORTFOLIO_ANALYZER_PROMPT


def create_portfolio_analysis_assistant():
    """
    Create a portfolio analysis assistant agent.

    Returns:
        Agent: Configured LangGraph agent with comprehensive portfolio analysis capabilities

    Raises:
        ConfigError: If OPENAI_API_KEY is not set
    """
    # Get OpenAI API key from centralized config
    openai_api_key = get_openai_api_key()

    # Initialize LLM
    llm = ChatOpenAI(
        model=DEFAULT_LLM_MODEL,
        temperature=0,  # Precise, analytical responses
        openai_api_key=openai_api_key
    )

    # Collect all portfolio analysis tools
    tools = [
        # Core portfolio tools
        get_portfolio_summary,
        analyze_portfolio_diversification,
        calculate_portfolio_performance,
        # Risk and comparison tools
        analyze_portfolio_risk,
        compare_portfolio_to_benchmark,
        # Recommendation tools
        get_rebalancing_recommendations,
        analyze_individual_position,
    ]

    # Create agent with tools
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=PORTFOLIO_ANALYZER_PROMPT
    )

    return agent


def ask_question(messages, verbose: bool = True):
    """
    Ask a portfolio analysis question and get an answer with conversation context.

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
        agent = create_portfolio_analysis_assistant()

        # Extract last question for display
        last_question = messages[-1]["content"] if messages else ""

        if verbose:
            print(f"\nYou: {last_question}\n")
            print("Portfolio Analyst: ", end="", flush=True)

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


# Example usage
if __name__ == "__main__":
    """
    Example demonstrating the Portfolio Analysis Agent.

    Make sure to set OPENAI_API_KEY environment variable.
    """
    import sys

    # Sample questions
    sample_questions = [
        "I have 10 shares of AAPL and 5 shares of MSFT. Can you analyze my portfolio?",
        "Check if my portfolio is well diversified: AAPL: 10, MSFT: 5, GOOGL: 3",
        "What's the risk profile of my portfolio with AAPL: 10, TSLA: 5?",
    ]

    # Check for command line arguments
    if len(sys.argv) > 1:
        # Use command line argument as question
        question = " ".join(sys.argv[1:])
        ask_question(question)
    else:
        # Show examples
        print("=" * 70)
        print("Portfolio Analysis Agent - Example Usage")
        print("=" * 70)
        print("\nThis agent can analyze your investment portfolio with tools for:")
        print("  • Portfolio summary and holdings overview")
        print("  • Diversification analysis (by position and sector)")
        print("  • Performance tracking over time")
        print("  • Risk analysis (volatility, Sharpe ratio, beta)")
        print("  • Benchmark comparison (vs S&P 500, Nasdaq, etc.)")
        print("  • Rebalancing recommendations")
        print("  • Individual position analysis")
        print("\nExample portfolio format: {'AAPL': 10, 'MSFT': 5, 'GOOGL': 3}")
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
        print("  python -m src.agents.portfolio_analysis 'Your question here'")
        print("\nExample:")
        print("  python -m src.agents.portfolio_analysis 'Analyze my portfolio: AAPL: 10, MSFT: 5, GOOGL: 3'")
