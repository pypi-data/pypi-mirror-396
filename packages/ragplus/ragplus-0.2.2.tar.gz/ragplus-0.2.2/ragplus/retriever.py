from typing import List, Dict, Tuple, Any
from .vectorstore import VectorStore


def retrieve(store: VectorStore, query: str, embed_fn, k=5):
    """
    Retrieve top-k most relevant texts for a query.
    
    Args:
        store: VectorStore instance
        query: Query string
        embed_fn: Function to embed the query
        k: Number of results to return
        
    Returns:
        List of tuples (text, metadata, score)
    """
    # Try to use is_query parameter for better embeddings
    try:
        query_vec = embed_fn([query], is_query=True).reshape(1, -1)
    except TypeError:
        # Fallback for embedders without is_query parameter
        query_vec = embed_fn([query]).reshape(1, -1)
    
    return store.search(query_vec, k)

