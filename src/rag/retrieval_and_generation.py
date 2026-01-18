from pydantic import BaseModel
from langchain.tools import tool

from .ingestion import get_vectorstore
from src.config import DEFAULT_RETRIEVAL_K
from src.prompts import RETRIEVE_TOOL_DESCRIPTION


class retrieveSchema(BaseModel):
    query: str


@tool("retrieve_tool", description=RETRIEVE_TOOL_DESCRIPTION)
def retrieve_tool(query: str) -> str:
    """
    Tool to retrieve relevant documents for a given query.

    Args:
        query (str): The user's query.
    Returns:
        str: Retrieved documents as a single string.
    """
    retrieved_docs = retrieve_relevant_documents(query)
    return retrieved_docs


def retrieve_relevant_documents(query: str, k: int = DEFAULT_RETRIEVAL_K) -> str:
    """
    Retrieve relevant documents from the vector store based on the query.

    Args:
        query (str): The user's query.
        k (int): Number of documents to retrieve. Defaults to value from config.

    Returns:
        str: Retrieved documents as a single string.
    """
    # Get the vector store
    vectorstore = get_vectorstore()

    # Perform similarity search
    retrieved_docs = vectorstore.similarity_search(query, k=k)

    # Combine retrieved documents into a single string
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )

    return serialized
