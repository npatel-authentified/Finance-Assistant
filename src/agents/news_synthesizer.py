"""
News Synthesizer Agent

This agent helps potential investors research investment opportunities by analyzing
financial news, assessing risks, and providing balanced due diligence.
"""

import sys
from pathlib import Path

# Add project root to Python path for direct execution
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.core.tools.news_synthesis import (
    discover_investment_opportunities,
    analyze_investment_risks,
    build_investment_thesis,
    compare_investment_options,
    assess_investment_timing,
    explain_news_for_investors,
    track_watchlist_news,
)
from src.config import get_openai_api_key, DEFAULT_LLM_MODEL, ConfigError
from src.prompts import NEWS_SYNTHESIZER_PROMPT


def create_news_synthesizer_assistant():
    """
    Create a news synthesizer assistant agent for potential investors.

    Returns:
        Agent: Configured LangGraph agent with news analysis and investment research capabilities

    Raises:
        ConfigError: If OPENAI_API_KEY is not set
    """
    # Get OpenAI API key from centralized config
    openai_api_key = get_openai_api_key()

    # Initialize LLM
    llm = ChatOpenAI(
        model=DEFAULT_LLM_MODEL,
        temperature=0.2,  # Lower temperature for more consistent analysis
        openai_api_key=openai_api_key
    )

    # Collect all news synthesis tools
    tools = [
        # Investment research tools
        discover_investment_opportunities,
        analyze_investment_risks,
        build_investment_thesis,
        compare_investment_options,
        assess_investment_timing,
        # News explanation tools
        explain_news_for_investors,
        track_watchlist_news,
    ]

    # Create agent with tools
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=NEWS_SYNTHESIZER_PROMPT
    )

    return agent


def ask_question(messages, verbose: bool = True):
    """
    Ask a news synthesis question and get an answer with conversation context.

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
        agent = create_news_synthesizer_assistant()

        # Extract last question for display
        last_question = messages[-1]["content"] if messages else ""

        if verbose:
            print(f"\nYou: {last_question}\n")
            print("News Research Assistant: ", end="", flush=True)

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
    Example demonstrating the News Synthesizer Agent.

    Make sure to set OPENAI_API_KEY environment variable.
    """
    import sys

    # Sample questions
    sample_questions = [
        "I'm thinking about investing in tech stocks. What opportunities look promising based on recent news?",
        "I'm considering investing in Tesla. Can you analyze the recent news and give me a balanced view of the risks?",
        "Should I invest in AAPL or MSFT? Compare them based on recent developments.",
        "I'm monitoring NVDA, AMD, and INTC. What's the latest news on these stocks?",
    ]

    # Check for command line arguments
    if len(sys.argv) > 1:
        # Use command line argument as question
        question = " ".join(sys.argv[1:])
        ask_question(question)
    else:
        # Show examples
        print("=" * 70)
        print("News Synthesizer Agent - Example Usage")
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
        print("  python -m src.agents.news_synthesizer 'Your question here'")
