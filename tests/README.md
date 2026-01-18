# Testing Guide

## Quick Start

### Install Test Dependencies

```bash
# Using uv
uv sync --extra dev

# Using pip
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py

# Run specific test
pytest tests/unit/test_config.py::TestAPIKeyRetrieval::test_get_openai_api_key_success

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests matching pattern
pytest -k "test_config"

# Run excluding slow tests
pytest -m "not slow"

# Run only edge case tests
pytest -m edge_case

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

## Test Organization

### Directory Structure

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── unit/                 # Unit tests (isolated)
│   ├── test_config.py
│   ├── test_prompts.py
│   ├── test_ingestion.py
│   └── test_retrieval.py
├── integration/          # Integration tests (multiple components)
│   ├── test_rag_pipeline.py
│   └── test_agent.py
└── fixtures/             # Test data files
    ├── sample.pdf
    ├── sample.txt
    └── sample.json
```

### Test Naming Convention

- **File**: `test_<module_name>.py`
- **Class**: `Test<Functionality>`
- **Function**: `test_<function>_<scenario>_<expected>`

**Examples:**
```python
def test_get_openai_api_key_success()  # Happy path
def test_get_openai_api_key_missing()  # Error case
def test_read_files_empty_directory()  # Edge case
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from src.config import get_openai_api_key, ConfigError


class TestAPIKeyRetrieval:
    """Group related tests in a class."""

    def test_get_openai_api_key_success(self, mock_env_vars):
        """Test successful API key retrieval."""
        # Arrange
        # (fixture provides setup)

        # Act
        key = get_openai_api_key()

        # Assert
        assert key == "test-openai-key-12345"
        assert isinstance(key, str)
        assert len(key) > 0

    def test_get_openai_api_key_missing(self, clear_env_vars):
        """Test error when API key is missing."""
        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            get_openai_api_key()

        # Verify error message
        assert "OPENAI_API_KEY" in str(exc_info.value)
```

### Using Fixtures

```python
def test_with_temp_directory(temp_dir):
    """Fixture provides a temporary directory."""
    file_path = temp_dir / "test.txt"
    file_path.write_text("content")
    assert file_path.exists()
    # temp_dir cleaned up automatically


def test_with_mocked_api(mock_openai_embeddings):
    """Fixture provides mocked OpenAI embeddings."""
    mock_openai_embeddings.embed_query.return_value = [0.1] * 1536
    # Use mock in test
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("pdf", ".pdf"),
    (".txt", ".txt"),
    ("docx", ".docx"),
])
def test_file_extension_normalization(input, expected):
    """Test multiple scenarios with same test logic."""
    result = normalize_extension(input)
    assert result == expected
```

### Marking Tests

```python
@pytest.mark.unit
def test_basic_function():
    """Mark as unit test."""
    pass


@pytest.mark.slow
def test_large_file_processing():
    """Mark as slow test."""
    pass


@pytest.mark.edge_case
def test_empty_input():
    """Mark as edge case test."""
    pass
```

## Best Practices

### 1. Test Independence
- Each test should be independent
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 2. Clear Test Names
```python
# Good
def test_read_files_returns_empty_string_for_empty_directory():
    pass

# Bad
def test_read_files_1():
    pass
```

### 3. Arrange-Act-Assert Pattern
```python
def test_function():
    # Arrange - Set up test data
    input_data = "test"

    # Act - Execute the function
    result = function_to_test(input_data)

    # Assert - Verify the result
    assert result == expected_output
```

### 4. Test One Thing
```python
# Good - Tests one scenario
def test_get_api_key_success():
    key = get_api_key()
    assert key is not None

# Bad - Tests multiple scenarios
def test_api_key():
    assert get_api_key() is not None
    with pytest.raises(Error):
        get_api_key_invalid()
```

### 5. Use Descriptive Assertions
```python
# Good
assert len(results) == 3, f"Expected 3 results, got {len(results)}"

# Better
expected = 3
actual = len(results)
assert actual == expected, f"Expected {expected} results, got {actual}"
```

## Mocking External Dependencies

### Mock OpenAI API
```python
from unittest.mock import patch

@patch('langchain_openai.ChatOpenAI')
def test_agent_creation(mock_llm):
    mock_llm.return_value.invoke.return_value = "response"
    agent = create_agent()
    # Test agent
```

### Mock Environment Variables
```python
def test_with_env_var(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    # Test code that uses API_KEY
```

### Mock File System
```python
def test_file_reading(tmp_path):
    # tmp_path is a pytest fixture providing temp directory
    file = tmp_path / "test.txt"
    file.write_text("content")
    # Test file reading
```

## Coverage

### View Coverage Report
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open report in browser
open htmlcov/index.html
```

### Coverage Goals
- **Overall**: > 80%
- **Critical modules (config, security)**: 100%
- **New features**: 100%

### Exclude from Coverage
```python
def debug_function():  # pragma: no cover
    """This function is only for debugging."""
    print("Debug output")
```

## Continuous Integration

### Pre-commit Checks
```bash
# Run before committing
pytest
pytest --cov=src --cov-report=term-missing
black src/ tests/
ruff src/ tests/
mypy src/
```

### CI Pipeline
```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Troubleshooting

### Import Errors
```bash
# Install package in editable mode
pip install -e .

# Or add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Fixture Not Found
- Check fixture is in `conftest.py` or imported
- Verify fixture scope (function, class, module, session)

### Test Discovery Issues
- Ensure test files start with `test_`
- Ensure test functions start with `test_`
- Check `pytest.ini` configuration

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
