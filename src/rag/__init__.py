"""RAG (Retrieval Augmented Generation) module for financial education content."""

from .ingestion import (
    setup_finance_rag,
    get_vectorstore,
    save_embeddings,
    get_finance_education_content
)

__all__ = [
    "setup_finance_rag",
    "get_vectorstore",
    "save_embeddings",
    "get_finance_education_content"
]
