"""
Financial Education Question & Answer Agent

This agent uses RAG (Retrieval Augmented Generation) to answer financial education
questions by retrieving relevant information from the vector database.
"""

import sys
from pathlib import Path

# Add project root to Python path for direct execution
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.rag.retrieval_and_generation import retrieve_tool
from src.config import get_openai_api_key, DEFAULT_LLM_MODEL, ConfigError
from src.prompts import FINANCIAL_ASSISTANT_PROMPT


def create_finance_assistant():
    """
    Create a financial education assistant agent.

    Returns:
        Agent: Configured LangGraph agent with retrieval capabilities

    Raises:
        ConfigError: If OPENAI_API_KEY is not set
    """
    # Get OpenAI API key from centralized config
    openai_api_key = get_openai_api_key()

    # Initialize LLM
    llm = ChatOpenAI(
        model=DEFAULT_LLM_MODEL,
        temperature=0,
        openai_api_key=openai_api_key
    )

    # Create agent with tools
    agent = create_agent(
        model=llm,
        tools=[retrieve_tool],
        system_prompt=FINANCIAL_ASSISTANT_PROMPT
    )

    return agent


def ask_question(messages, verbose: bool = True):
    """
    Ask a financial education question and get an answer with conversation context.

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
        agent = create_finance_assistant()

        # Extract last question for display
        last_question = messages[-1]["content"] if messages else ""

        if verbose:
            print(f"\nQuestion: {last_question}\n")
            print("Assistant: ", end="", flush=True)

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
    Example demonstrating the Q&A agent.

    Make sure to:
    1. Set up the vector database first (run ingestion.py)
    2. Set OPENAI_API_KEY and PINECONE_API_KEY environment variables
    """
    import sys

    # Sample questions
    sample_questions = [
        "How to retire with tax free early with smart financial planning?",
        "What is compound interest and how does it work?",
        "How do I create a budget for my monthly expenses?",
    ]

    # Use command line argument if provided, otherwise use samples
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        ask_question(question)
    else:
        print("=" * 60)
        print("Financial Education Q&A Agent - Example Usage")
        print("=" * 60)

        for i, question in enumerate(sample_questions, 1):
            print(f"\n{'='*60}")
            print(f"Example {i}/{len(sample_questions)}")
            print(f"{'='*60}")

            ask_question(question)

            if i < len(sample_questions):
                input("\nPress Enter to continue to next question...")

        print("\n" + "=" * 60)
        print("Example Complete!")
        print("=" * 60)
        print("\nTo ask your own question, run:")
        print("  python -m src.agents.ques_ans 'Your question here'")