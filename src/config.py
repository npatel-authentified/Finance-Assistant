"""
Configuration Module

Centralized configuration management for API keys and environment variables.
Follows DRY principle by providing single source of truth for all configuration.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigError(Exception):
    """Raised when configuration is missing or invalid."""
    pass


def get_openai_api_key() -> str:
    """
    Get OpenAI API key from environment variables.

    Returns:
        str: The OpenAI API key

    Raises:
        ConfigError: If OPENAI_API_KEY environment variable is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it before using this application:\n"
            "  export OPENAI_API_KEY='your-api-key-here'\n"
            "Or add it to your .env file."
        )
    return api_key


def get_pinecone_api_key() -> str:
    """
    Get Pinecone API key from environment variables.

    Returns:
        str: The Pinecone API key

    Raises:
        ConfigError: If PINECONE_API_KEY environment variable is not set
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ConfigError(
            "PINECONE_API_KEY environment variable is not set. "
            "Please set it before using this application:\n"
            "  export PINECONE_API_KEY='your-api-key-here'\n"
            "Or add it to your .env file."
        )
    return api_key


def get_config_value(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get a configuration value from environment variables.

    Args:
        key: The environment variable key
        default: Default value if key is not found
        required: If True, raise ConfigError when key is missing

    Returns:
        The configuration value or default

    Raises:
        ConfigError: If required=True and key is not found
    """
    value = os.getenv(key, default)

    if required and value is None:
        raise ConfigError(
            f"{key} environment variable is required but not set. "
            f"Please set it in your environment or .env file."
        )

    return value


# Application configuration constants
INDEX_NAME = get_config_value("PINECONE_INDEX_NAME", default="finance-education-index")
DEFAULT_CHUNK_SIZE = int(get_config_value("CHUNK_SIZE", default="300"))
DEFAULT_CHUNK_OVERLAP = int(get_config_value("CHUNK_OVERLAP", default="100"))
DEFAULT_LLM_MODEL = get_config_value("LLM_MODEL", default="gpt-4o-mini")
DEFAULT_EMBEDDING_MODEL = get_config_value("EMBEDDING_MODEL", default="text-embedding-3-small")
DEFAULT_RETRIEVAL_K = int(get_config_value("RETRIEVAL_K", default="5"))

# Context window management configuration
MAX_CONTEXT_MESSAGES = int(get_config_value("MAX_CONTEXT_MESSAGES", default="10"))
MAX_CONTEXT_TOKENS = int(get_config_value("MAX_CONTEXT_TOKENS", default="4000"))
CONTEXT_TRIMMING_STRATEGY = get_config_value("CONTEXT_TRIMMING_STRATEGY", default="last")


def validate_config() -> bool:
    """
    Validate that all required configuration is present.

    Returns:
        bool: True if all required config is valid

    Raises:
        ConfigError: If any required configuration is missing
    """
    try:
        get_openai_api_key()
        get_pinecone_api_key()
        return True
    except ConfigError as e:
        raise ConfigError(f"Configuration validation failed: {str(e)}")


if __name__ == "__main__":
    """Test configuration loading."""
    print("Testing configuration...")
    print("=" * 60)

    try:
        print(f"✓ INDEX_NAME: {INDEX_NAME}")
        print(f"✓ CHUNK_SIZE: {DEFAULT_CHUNK_SIZE}")
        print(f"✓ CHUNK_OVERLAP: {DEFAULT_CHUNK_OVERLAP}")
        print(f"✓ LLM_MODEL: {DEFAULT_LLM_MODEL}")
        print(f"✓ EMBEDDING_MODEL: {DEFAULT_EMBEDDING_MODEL}")
        print(f"✓ RETRIEVAL_K: {DEFAULT_RETRIEVAL_K}")

        openai_key = get_openai_api_key()
        print(f"✓ OPENAI_API_KEY: {openai_key[:8]}...{openai_key[-4:]}")

        pinecone_key = get_pinecone_api_key()
        print(f"✓ PINECONE_API_KEY: {pinecone_key[:8]}...{pinecone_key[-4:]}")

        print("\n" + "=" * 60)
        print("✓ All configuration validated successfully!")

    except ConfigError as e:
        print(f"\n✗ Configuration Error: {e}")
        exit(1)
