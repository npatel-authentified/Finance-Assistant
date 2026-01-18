"""
Shared test fixtures and configuration for pytest.

This file contains fixtures that are available to all tests.
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock


# Environment fixtures
@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key-12345")
    monkeypatch.setenv("PINECONE_API_KEY", "test-pinecone-key-67890")
    monkeypatch.setenv("PINECONE_INDEX_NAME", "test-finance-index")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("CHUNK_SIZE", "300")
    monkeypatch.setenv("CHUNK_OVERLAP", "100")
    return {
        "OPENAI_API_KEY": "test-openai-key-12345",
        "PINECONE_API_KEY": "test-pinecone-key-67890",
    }


@pytest.fixture
def clear_env_vars(monkeypatch):
    """Clear all environment variables for testing missing config."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("PINECONE_API_KEY", raising=False)
    monkeypatch.delenv("PINECONE_INDEX_NAME", raising=False)


# File system fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    content = "This is a test document about personal finance.\nIt contains information about budgeting and saving."
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing."""
    file_path = temp_dir / "sample.json"
    content = '{"topic": "investing", "description": "Guide to stock market investing"}'
    file_path.write_text(content)
    return file_path


@pytest.fixture
def empty_file(temp_dir):
    """Create an empty file for testing."""
    file_path = temp_dir / "empty.txt"
    file_path.touch()
    return file_path


@pytest.fixture
def large_text_file(temp_dir):
    """Create a large text file for testing."""
    file_path = temp_dir / "large.txt"
    # Create a 1MB file
    content = "Financial education content.\n" * 50000
    file_path.write_text(content)
    return file_path


@pytest.fixture
def unicode_filename_file(temp_dir):
    """Create a file with unicode characters in the name."""
    file_path = temp_dir / "finance_文档.txt"
    content = "Content with unicode filename"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def nested_directory(temp_dir):
    """Create a nested directory structure with files."""
    subdir1 = temp_dir / "level1" / "level2" / "level3"
    subdir1.mkdir(parents=True)
    (subdir1 / "deep.txt").write_text("Deeply nested content")
    (temp_dir / "root.txt").write_text("Root level content")
    (temp_dir / "level1" / "mid.txt").write_text("Mid level content")
    return temp_dir


# Mock fixtures for external services
@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings for testing."""
    mock = MagicMock()
    # Mock embedding vector (1536 dimensions for text-embedding-3-small)
    mock.embed_query.return_value = [0.1] * 1536
    mock.embed_documents.return_value = [[0.1] * 1536]
    return mock


@pytest.fixture
def mock_pinecone_client():
    """Mock Pinecone client for testing."""
    mock_client = MagicMock()

    # Mock list_indexes
    mock_indexes = MagicMock()
    mock_indexes.names.return_value = []
    mock_client.list_indexes.return_value = mock_indexes

    # Mock index creation
    mock_client.create_index.return_value = None

    # Mock index operations
    mock_index = MagicMock()
    mock_stats = {
        'total_vector_count': 0,
        'dimension': 1536
    }
    mock_index.describe_index_stats.return_value = mock_stats
    mock_client.Index.return_value = mock_index

    return mock_client


@pytest.fixture
def mock_vectorstore():
    """Mock PineconeVectorStore for testing."""
    mock = MagicMock()

    # Mock similarity search
    mock_doc = Mock()
    mock_doc.page_content = "Sample financial content about budgeting"
    mock_doc.metadata = {"source": "test.pdf", "page": 1}
    mock.similarity_search.return_value = [mock_doc]

    # Mock from_documents
    mock.from_documents = MagicMock(return_value=mock)

    return mock


@pytest.fixture
def mock_documents():
    """Create mock LangChain documents for testing."""
    docs = []
    for i in range(5):
        doc = Mock()
        doc.page_content = f"This is test document {i} about financial topics."
        doc.metadata = {"source": f"doc{i}.pdf", "page": i}
        docs.append(doc)
    return docs


@pytest.fixture
def mock_llm():
    """Mock ChatOpenAI LLM for testing."""
    mock = MagicMock()
    mock.invoke.return_value = "This is a mock LLM response about financial education."
    return mock


# Test data fixtures
@pytest.fixture
def sample_query():
    """Sample user query for testing."""
    return "How do I create a monthly budget?"


@pytest.fixture
def edge_case_queries():
    """Collection of edge case queries for testing."""
    return {
        "empty": "",
        "long": "How do I " + ("save money " * 1000),
        "special_chars": "What's the 401(k) & IRA difference?",
        "unicode": "Como puedo ahorrar dinero? 💰",
        "code": "```python\nprint('test')\n```",
        "whitespace": "   \n  \t  ",
        "sql_injection": "'; DROP TABLE users; --",
        "xss": "<script>alert('xss')</script>",
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "edge_case: marks tests as edge case tests"
    )
