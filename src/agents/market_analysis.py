"""
Market Analysis Agent

This agent helps users analyze market trends, sectors, individual stocks, and overall market sentiment
using comprehensive technical and fundamental analysis tools.
"""

import sys
from pathlib import Path

# Add project root to Python path for direct execution
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.core.tools.market_analysis import (
    get_market_overview,
    analyze_sector_performance,
    get_stock_technicals,
    compare_stock_fundamentals,
    get_market_sentiment,
    get_stock_news,
    get_earnings_calendar,
    analyze_stock_momentum,
)
from src.config import get_openai_api_key, DEFAULT_LLM_MODEL, ConfigError
from src.prompts import MARKET_ANALYSIS_PROMPT


def create_market_analysis_assistant():
    """
    Create a market analysis assistant agent.

    Returns:
        Agent: Configured LangGraph agent with comprehensive market analysis capabilities

    Raises:
        ConfigError: If OPENAI_API_KEY is not set
    """
    # Get OpenAI API key from centralized config
    openai_api_key = get_openai_api_key()

    # Initialize LLM
    llm = ChatOpenAI(
        model=DEFAULT_LLM_MODEL,
        temperature=0.2,  # Slightly higher for more natural explanations
        openai_api_key=openai_api_key
    )

    # Collect all market analysis tools
    tools = [
        # Market-level tools
        get_market_overview,
        analyze_sector_performance,
        get_market_sentiment,
        # Stock analysis tools
        get_stock_technicals,
        compare_stock_fundamentals,
        analyze_stock_momentum,
        # Information tools
        get_stock_news,
        get_earnings_calendar,
    ]

    # Create agent with tools
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=MARKET_ANALYSIS_PROMPT
    )

    return agent


def ask_question(messages, verbose: bool = True):
    """
    Ask a market analysis question and get an answer with conversation context.

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
        agent = create_market_analysis_assistant()

        # Extract last question for display
        last_question = messages[-1]["content"] if messages else ""

        if verbose:
            print(f"\nYou: {last_question}\n")
            print("Market Analyst: ", end="", flush=True)

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
    Example demonstrating the Market Analysis Agent.

    Make sure to set OPENAI_API_KEY environment variable.
    """
    import sys

    # Sample questions
    sample_questions = [
        "What's the current market overview? How are the major indices doing?",
        "Analyze the technology sector performance over the past month",
        "Give me a technical analysis of AAPL stock",
        "Compare the fundamentals of AAPL, MSFT, and GOOGL",
    ]

    # Check for command line arguments
    if len(sys.argv) > 1:
        # Use command line argument as question
        question = " ".join(sys.argv[1:])
        ask_question(question)
    else:
        # Show examples
        print("=" * 70)
        print("Market Analysis Agent - Example Usage")
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
        print("  python -m src.agents.market_analysis 'Your question here'")
