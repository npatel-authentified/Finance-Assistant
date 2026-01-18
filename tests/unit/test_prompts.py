"""
Unit tests for src/prompts.py

Tests prompt management including:
- Prompt retrieval
- Template formatting
- Edge cases
"""

import pytest
from src.prompts import (
    FINANCIAL_ASSISTANT_PROMPT,
    RETRIEVE_TOOL_DESCRIPTION,
    get_prompt,
    format_prompt,
    PERSONALIZED_GREETING_TEMPLATE,
)


class TestPromptConstants:
    """Test that prompt constants exist and are valid."""

    def test_financial_assistant_prompt_exists(self):
        """Test FINANCIAL_ASSISTANT_PROMPT exists and is non-empty."""
        assert isinstance(FINANCIAL_ASSISTANT_PROMPT, str)
        assert len(FINANCIAL_ASSISTANT_PROMPT) > 0
        assert "financial education assistant" in FINANCIAL_ASSISTANT_PROMPT.lower()

    def test_retrieve_tool_description_exists(self):
        """Test RETRIEVE_TOOL_DESCRIPTION exists and is non-empty."""
        assert isinstance(RETRIEVE_TOOL_DESCRIPTION, str)
        assert len(RETRIEVE_TOOL_DESCRIPTION) > 0

    def test_prompts_contain_expected_keywords(self):
        """Test that prompts contain expected domain keywords."""
        assert any(
            keyword in FINANCIAL_ASSISTANT_PROMPT.lower()
            for keyword in ["financial", "finance", "education"]
        )


class TestGetPrompt:
    """Test get_prompt function."""

    def test_get_valid_prompt(self):
        """Test retrieving a valid prompt by name."""
        prompt = get_prompt("financial_assistant")

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert prompt == FINANCIAL_ASSISTANT_PROMPT

    def test_get_invalid_prompt_raises_error(self):
        """Test that invalid prompt name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_prompt("nonexistent_prompt")

        assert "not found" in str(exc_info.value).lower()
        assert "nonexistent_prompt" in str(exc_info.value)

    def test_get_prompt_returns_correct_types(self):
        """Test that all retrievable prompts return strings."""
        prompt_names = [
            "financial_assistant",
            "budget_advisor",
            "investment_advisor",
            "debt_management"
        ]

        for name in prompt_names:
            prompt = get_prompt(name)
            assert isinstance(prompt, str)
            assert len(prompt) > 0


class TestFormatPrompt:
    """Test format_prompt function."""

    def test_format_with_valid_variables(self):
        """Test formatting template with valid variables."""
        template = "Hello {name}, you have {count} messages"
        result = format_prompt(template, name="Alice", count=5)

        assert result == "Hello Alice, you have 5 messages"

    def test_format_with_greeting_template(self):
        """Test formatting the personalized greeting template."""
        result = format_prompt(
            PERSONALIZED_GREETING_TEMPLATE,
            user_name="Bob",
            topics="investing and budgeting"
        )

        assert "Bob" in result
        assert "investing and budgeting" in result

    def test_format_with_missing_variable_raises_error(self):
        """Test that missing template variable raises KeyError."""
        template = "Hello {name}, you have {count} messages"

        with pytest.raises(KeyError):
            format_prompt(template, name="Alice")  # Missing 'count'

    def test_format_with_extra_variables(self):
        """Test formatting with extra variables (should be ignored)."""
        template = "Hello {name}"
        result = format_prompt(template, name="Alice", extra="ignored")

        assert result == "Hello Alice"


@pytest.mark.edge_case
class TestPromptEdgeCases:
    """Test edge cases for prompts."""

    def test_empty_prompt_name(self):
        """Test empty string as prompt name."""
        with pytest.raises(ValueError):
            get_prompt("")

    def test_none_prompt_name(self):
        """Test None as prompt name."""
        with pytest.raises((ValueError, TypeError)):
            get_prompt(None)

    def test_prompt_name_case_sensitivity(self):
        """Test that prompt names are case-sensitive."""
        # Lowercase should work
        prompt1 = get_prompt("financial_assistant")
        assert prompt1 is not None

        # Uppercase should fail
        with pytest.raises(ValueError):
            get_prompt("FINANCIAL_ASSISTANT")

    def test_format_empty_template(self):
        """Test formatting an empty template."""
        result = format_prompt("", name="Alice")

        assert result == ""

    def test_format_with_special_characters(self):
        """Test template with special characters."""
        template = "Email: {email}, Cost: ${price}"
        result = format_prompt(template, email="test@example.com", price="99.99")

        assert result == "Email: test@example.com, Cost: $99.99"

    def test_format_with_unicode(self):
        """Test template formatting with unicode characters."""
        template = "User: {name}, Message: {msg}"
        result = format_prompt(template, name="José", msg="Hello! 👋")

        assert "José" in result
        assert "👋" in result

    def test_format_with_newlines(self):
        """Test template with newline characters."""
        template = "Line 1: {line1}\nLine 2: {line2}"
        result = format_prompt(template, line1="First", line2="Second")

        assert "Line 1: First" in result
        assert "Line 2: Second" in result
        assert "\n" in result

    def test_format_with_very_long_values(self):
        """Test formatting with very long values."""
        template = "Content: {content}"
        long_content = "x" * 10000
        result = format_prompt(template, content=long_content)

        assert len(result) > 10000
        assert long_content in result

    def test_prompt_immutability(self):
        """Test that getting a prompt doesn't modify the original."""
        original = get_prompt("financial_assistant")
        retrieved = get_prompt("financial_assistant")

        assert original == retrieved
        assert original is not retrieved  # Different objects

    def test_format_with_numeric_values(self):
        """Test template formatting with numeric types."""
        template = "Count: {count}, Price: {price}, Active: {active}"
        result = format_prompt(template, count=42, price=99.99, active=True)

        assert "42" in result
        assert "99.99" in result
        assert "True" in result

    def test_format_with_nested_braces(self):
        """Test template with nested braces."""
        template = "Data: {{key: {value}}}"
        result = format_prompt(template, value="test")

        assert "{key: test}" in result

    def test_multiple_same_variable_in_template(self):
        """Test template with same variable multiple times."""
        template = "{name} likes {name}'s job"
        result = format_prompt(template, name="Alice")

        assert result == "Alice likes Alice's job"
