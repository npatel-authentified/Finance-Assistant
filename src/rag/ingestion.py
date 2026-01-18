"""
Finance Education RAG Module

This module provides RAG (Retrieval Augmented Generation) capabilities
for financial education content using Pinecone vector database.

Key Features:
- Automatic duplicate prevention: Checks if embeddings already exist
- Supports multiple document formats via PyPDFDirectoryLoader
- Efficient chunking with RecursiveCharacterTextSplitter
- OpenAI embeddings for semantic search
- Pinecone vector store for fast retrieval

Usage:
    # One-time setup (creates embeddings if they don't exist)
    from src.rag.ingestion import setup_finance_rag
    vectorstore = setup_finance_rag("./financial_docs")

    # Query the vector store
    results = vectorstore.similarity_search("What is compound interest?", k=3)

    # Force re-indexing if documents changed
    vectorstore = setup_finance_rag("./financial_docs", force_reindex=True)

    # Get existing vector store without re-indexing
    from src.rag.ingestion import get_vectorstore
    vectorstore = get_vectorstore()
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add project root to Python path for direct execution
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from src.config import (
    get_openai_api_key,
    get_pinecone_api_key,
    INDEX_NAME,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP
)

# Module-level cache
_pinecone_client: Optional[Pinecone] = None
_openai_embeddings: Optional[OpenAIEmbeddings] = None


def _get_pinecone_client() -> Pinecone:
    """
    Get or initialize the Pinecone client with proper error handling.

    Returns:
        Pinecone: Initialized Pinecone client

    Raises:
        ConfigError: If PINECONE_API_KEY environment variable is not set
    """
    global _pinecone_client

    if _pinecone_client is not None:
        return _pinecone_client

    api_key = get_pinecone_api_key()
    _pinecone_client = Pinecone(api_key=api_key)
    return _pinecone_client


def _get_openai_embeddings() -> OpenAIEmbeddings:
    """
    Get OpenAI embeddings instance with proper error handling.

    Returns:
        OpenAIEmbeddings: Initialized embeddings instance

    Raises:
        ConfigError: If OPENAI_API_KEY environment variable is not set
    """
    global _openai_embeddings

    if _openai_embeddings is not None:
        return _openai_embeddings

    api_key = get_openai_api_key()
    _openai_embeddings = OpenAIEmbeddings(
        model=DEFAULT_EMBEDDING_MODEL,
        openai_api_key=api_key
    )
    return _openai_embeddings

def get_finance_education_content(
    folder_path: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[str]: 
    """
    Split financial education content into smaller chunks.

    Args:
        contents: List of content strings to split
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks

    Returns:
        List of content chunks
    """
    # 1. Load all PDFs from the directory
    loader = PyPDFDirectoryLoader(folder_path)
    docs = loader.load()
    
    # 2. Define your splitting strategy
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    # 3. Split all documents at once
    all_chunks = text_splitter.split_documents(docs)

    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks

 
def save_embeddings(documents: List, force_reindex: bool = False) -> PineconeVectorStore:
    """
    Save document embeddings to Pinecone vector database.

    This function checks if embeddings already exist in the vector database
    and only creates/updates them if necessary.

    Args:
        documents: List of LangChain Document objects to embed and store
        force_reindex: If True, delete existing index and recreate it.
                      If False, skip if index already has documents.

    Returns:
        PineconeVectorStore: The vector store instance

    Raises:
        ValueError: If required API keys are not set
    """
    # Get clients with error handling
    pc = _get_pinecone_client()
    embeddings = _get_openai_embeddings()

    # Check if index exists
    existing_indexes = pc.list_indexes().names()
    index_exists = INDEX_NAME in existing_indexes

    if index_exists:
        # Get index stats to check if it has documents
        index = pc.Index(INDEX_NAME)
        stats = index.describe_index_stats()
        vector_count = stats.get('total_vector_count', 0)

        if vector_count > 0 and not force_reindex:
            print(f"Index '{INDEX_NAME}' already exists with {vector_count} vectors. Skipping indexing.")
            print("Use force_reindex=True to recreate the index.")

            # Return existing vector store
            vectorstore = PineconeVectorStore(
                index_name=INDEX_NAME,
                embedding=embeddings
            )
            return vectorstore

        if force_reindex:
            print(f"Deleting existing index '{INDEX_NAME}' with {vector_count} vectors...")
            pc.delete_index(INDEX_NAME)
            index_exists = False

    # Create index if it doesn't exist
    if not index_exists:
        print(f"Creating new Pinecone index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,  # Standard for OpenAI text-embedding-3-small
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        print("Index created successfully.")

    # Create embeddings and store in Pinecone
    print(f"Embedding and storing {len(documents)} documents in Pinecone...")
    vectorstore = PineconeVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        index_name=INDEX_NAME
    )

    # Verify storage
    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()
    print(f"Successfully stored {stats.get('total_vector_count', 0)} vectors in Pinecone.")

    return vectorstore


def get_vectorstore() -> PineconeVectorStore:
    """
    Get existing Pinecone vector store instance.

    Returns:
        PineconeVectorStore: The vector store instance

    Raises:
        ValueError: If the index doesn't exist or API keys are not set
    """
    pc = _get_pinecone_client()
    embeddings = _get_openai_embeddings()

    if INDEX_NAME not in pc.list_indexes().names():
        raise ValueError(
            f"Index '{INDEX_NAME}' does not exist. "
            "Please create embeddings first using setup_finance_rag() or save_embeddings()."
        )

    vectorstore = PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=embeddings
    )

    return vectorstore


def setup_finance_rag(folder_path: str, force_reindex: bool = False) -> PineconeVectorStore:
    """
    Complete workflow to set up the finance education RAG system.

    This function:
    1. Loads and chunks documents from the folder
    2. Checks if embeddings already exist
    3. Creates/updates embeddings in Pinecone if needed
    4. Returns the vector store for querying

    Args:
        folder_path: Path to directory containing financial education documents
        force_reindex: If True, recreate the index even if it exists

    Returns:
        PineconeVectorStore: Ready-to-use vector store for querying

    Example:
        >>> vectorstore = setup_finance_rag("./financial_docs")
        >>> results = vectorstore.similarity_search("What is compound interest?", k=3)
    """
    print("=" * 60)
    print("Setting up Finance Education RAG System")
    print("=" * 60)

    # Step 1: Load and chunk documents
    print("\n[1/2] Loading and chunking documents...")
    documents = get_finance_education_content(folder_path)

    # Step 2: Create/update embeddings in Pinecone
    print("\n[2/2] Setting up vector database...")
    vectorstore = save_embeddings(documents, force_reindex=force_reindex)

    print("\n" + "=" * 60)
    print("RAG System Setup Complete!")
    print("=" * 60)

    return vectorstore


# Example usage
if __name__ == "__main__":
    """
    Example demonstrating the complete RAG workflow.

    Make sure to set environment variables:
    - PINECONE_API_KEY
    - OPENAI_API_KEY
    """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python financeEd_rag.py <folder_path> [--force-reindex]")
        print("\nExample:")
        print("  python financeEd_rag.py ./financial_docs")
        print("  python financeEd_rag.py ./financial_docs --force-reindex")
        sys.exit(1)

    folder_path = 'src/data/resources/'
    force_reindex = "--force-reindex" in sys.argv

    # Setup the RAG system
    vectorstore = setup_finance_rag(folder_path, force_reindex=force_reindex)

    # Example query
    print("\n" + "=" * 60)
    print("Testing Vector Store with Sample Queries")
    print("=" * 60)

    sample_queries = [
        "What is compound interest?",
        "How do I create a budget?",
        "What are the benefits of diversification?"
    ]

    for query in sample_queries:
        print(f"\nQuery: {query}")
        results = vectorstore.similarity_search(query, k=2)
        print(f"Found {len(results)} relevant chunks:")
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.page_content[:100]}...")

    print("\n" + "=" * 60)
    print("Example Complete!")
    print("=" * 60)
