"""
Unit tests for src/config.py

Tests configuration management including:
- API key retrieval
- Configuration validation
- Edge cases and error handling
"""

import pytest
from src.config import (
    get_openai_api_key,
    get_pinecone_api_key,
    get_config_value,
    validate_config,
    ConfigError,
    INDEX_NAME,
    DEFAULT_LLM_MODEL,
)


class TestAPIKeyRetrieval:
    """Test API key getter functions."""

    def test_get_openai_api_key_success(self, mock_env_vars):
        """Test successful OpenAI API key retrieval."""
        key = get_openai_api_key()
        assert key == "test-openai-key-12345"
        assert isinstance(key, str)
        assert len(key) > 0

    def test_get_openai_api_key_missing(self, clear_env_vars):
        """Test OpenAI API key retrieval when not set."""
        with pytest.raises(ConfigError) as exc_info:
            get_openai_api_key()

        assert "OPENAI_API_KEY" in str(exc_info.value)
        assert "not set" in str(exc_info.value)

    def test_get_pinecone_api_key_success(self, mock_env_vars):
        """Test successful Pinecone API key retrieval."""
        key = get_pinecone_api_key()
        assert key == "test-pinecone-key-67890"
        assert isinstance(key, str)
        assert len(key) > 0

    def test_get_pinecone_api_key_missing(self, clear_env_vars):
        """Test Pinecone API key retrieval when not set."""
        with pytest.raises(ConfigError) as exc_info:
            get_pinecone_api_key()

        assert "PINECONE_API_KEY" in str(exc_info.value)
        assert "not set" in str(exc_info.value)


class TestConfigValueRetrieval:
    """Test generic configuration value retrieval."""

    def test_get_config_value_with_default(self, clear_env_vars):
        """Test getting config value with default when not set."""
        value = get_config_value("NON_EXISTENT_KEY", default="default_value")
        assert value == "default_value"

    def test_get_config_value_without_default(self, clear_env_vars):
        """Test getting config value without default when not set."""
        value = get_config_value("NON_EXISTENT_KEY")
        assert value is None

    def test_get_config_value_required_missing(self, clear_env_vars):
        """Test getting required config value when not set raises error."""
        with pytest.raises(ConfigError) as exc_info:
            get_config_value("REQUIRED_KEY", required=True)

        assert "REQUIRED_KEY" in str(exc_info.value)
        assert "required" in str(exc_info.value).lower()

    def test_get_config_value_existing(self, mock_env_vars):
        """Test getting existing config value."""
        value = get_config_value("OPENAI_API_KEY")
        assert value == "test-openai-key-12345"


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_config_success(self, mock_env_vars):
        """Test successful configuration validation."""
        assert validate_config() is True

    def test_validate_config_missing_openai(self, monkeypatch):
        """Test validation fails with missing OpenAI key."""
        monkeypatch.setenv("PINECONE_API_KEY", "test-key")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(ConfigError) as exc_info:
            validate_config()

        assert "OPENAI_API_KEY" in str(exc_info.value)

    def test_validate_config_missing_pinecone(self, monkeypatch):
        """Test validation fails with missing Pinecone key."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.delenv("PINECONE_API_KEY", raising=False)

        with pytest.raises(ConfigError) as exc_info:
            validate_config()

        assert "PINECONE_API_KEY" in str(exc_info.value)


class TestConfigConstants:
    """Test configuration constants."""

    def test_index_name_exists(self):
        """Test INDEX_NAME constant exists and is a string."""
        assert isinstance(INDEX_NAME, str)
        assert len(INDEX_NAME) > 0

    def test_default_llm_model_exists(self):
        """Test DEFAULT_LLM_MODEL constant exists and is valid."""
        assert isinstance(DEFAULT_LLM_MODEL, str)
        assert len(DEFAULT_LLM_MODEL) > 0


@pytest.mark.edge_case
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string_api_key(self, monkeypatch):
        """Test that empty string API key is treated as missing."""
        monkeypatch.setenv("OPENAI_API_KEY", "")

        with pytest.raises(ConfigError):
            get_openai_api_key()

    def test_whitespace_api_key(self, monkeypatch):
        """Test API key with only whitespace."""
        monkeypatch.setenv("OPENAI_API_KEY", "   \t\n  ")

        # Whitespace-only should be treated as valid (though unusual)
        # as it's technically a string value
        key = get_openai_api_key()
        assert isinstance(key, str)

    def test_very_long_api_key(self, monkeypatch):
        """Test handling of very long API keys."""
        long_key = "x" * 10000
        monkeypatch.setenv("OPENAI_API_KEY", long_key)

        key = get_openai_api_key()
        assert key == long_key
        assert len(key) == 10000

    def test_api_key_with_special_characters(self, monkeypatch):
        """Test API keys with special characters."""
        special_key = "key-with-$pecial_ch@rs!#%"
        monkeypatch.setenv("OPENAI_API_KEY", special_key)

        key = get_openai_api_key()
        assert key == special_key

    def test_unicode_in_config_value(self, monkeypatch):
        """Test configuration values with unicode characters."""
        unicode_value = "测试_テスト_🔑"
        monkeypatch.setenv("TEST_UNICODE", unicode_value)

        value = get_config_value("TEST_UNICODE")
        assert value == unicode_value

    def test_config_value_type_coercion(self, monkeypatch):
        """Test that numeric strings are returned as strings."""
        monkeypatch.setenv("NUMERIC_CONFIG", "12345")

        value = get_config_value("NUMERIC_CONFIG")
        assert value == "12345"
        assert isinstance(value, str)

    def test_none_vs_empty_string(self, clear_env_vars):
        """Test difference between None and empty string."""
        # Not set should return None
        value1 = get_config_value("NOT_SET")
        assert value1 is None

        # Default should be used
        value2 = get_config_value("NOT_SET", default="")
        assert value2 == ""
        assert value2 is not None
