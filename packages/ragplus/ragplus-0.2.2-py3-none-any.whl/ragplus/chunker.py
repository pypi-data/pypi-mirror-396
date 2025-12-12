from typing import List
import re

try:
    import nltk
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


def chunk_text(text, size=500, overlap=50, strategy="fixed", embedder=None):
    """
    Split text into chunks using various strategies.
    
    Args:
        text: Input text to chunk
        size: Maximum chunk size in characters (for fixed strategy)
        overlap: Number of characters to overlap between chunks (for fixed strategy)
        strategy: Chunking strategy - "fixed", "sentence", "markdown", "heading", or "semantic"
        embedder: Embedder instance (required for semantic strategy)
        
    Returns:
        List of text chunks
    """
    text = text.strip()
    if not text:
        return []

    if strategy == "fixed":
        return _chunk_fixed(text, size, overlap)
    elif strategy == "sentence":
        return _chunk_sentence(text, size)
    elif strategy == "markdown":
        return _chunk_markdown(text)
    elif strategy == "heading":
        return _chunk_heading(text)
    elif strategy == "semantic":
        if embedder is None:
            raise ValueError("Embedder required for semantic chunking strategy")
        return _chunk_semantic(text, embedder, max_chunk_size=size)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def _chunk_fixed(text, size=500, overlap=50):
    """Fixed-size chunking with overlap."""
    if size <= 0:
        raise ValueError("chunk size must be > 0")

    if overlap >= size:
        raise ValueError("overlap must be < chunk size")

    chunks = []
    n = len(text)

    start = 0
    while start < n:
        end = min(start + size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward, not backward
        next_start = start + size - overlap
        if next_start <= start:  # safety check
            break
        start = next_start

    return chunks


def _chunk_sentence(text, max_sentences=5, overlap_sentences=1):
    """
    Sentence-based chunking with overlap for better context preservation.
    
    Args:
        text: Input text
        max_sentences: Maximum sentences per chunk
        overlap_sentences: Number of sentences to overlap between chunks
        
    Returns:
        List of text chunks with overlapping sentences
    """
    if not NLTK_AVAILABLE:
        # Fallback to simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
    else:
        try:
            sentences = nltk.sent_tokenize(text)
        except LookupError:
            # Download punkt tokenizer if not available
            try:
                nltk.download('punkt', quiet=True)
                sentences = nltk.sent_tokenize(text)
            except:
                # Fallback
                sentences = re.split(r'[.!?]+', text)
    
    # Clean sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return []
    
    # Create chunks with overlap
    chunks = []
    i = 0
    
    while i < len(sentences):
        # Get chunk sentences
        chunk_sents = sentences[i:i + max_sentences]
        
        if chunk_sents:
            chunks.append(' '.join(chunk_sents))
        
        # Move forward by (max_sentences - overlap_sentences)
        # This creates overlap between consecutive chunks
        step = max(1, max_sentences - overlap_sentences)
        i += step
    
    return chunks



def _chunk_markdown(text):
    """Markdown-aware chunking based on headers and sections."""
    # Split by markdown headers
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    
    for line in lines:
        # Check if line is a header
        if re.match(r'^#{1,6}\s', line):
            # Save previous chunk
            if current_chunk:
                chunks.append('\n'.join(current_chunk).strip())
            # Start new chunk with header
            current_chunk = [line]
        else:
            current_chunk.append(line)
    
    # Add final chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk).strip()
        if chunk_text:
            chunks.append(chunk_text)
    
    return chunks if chunks else [text]


def _chunk_heading(text):
    """Heading-based chunking for structured documents."""
    # Split by common heading patterns
    heading_pattern = r'\n(?=[A-Z][A-Za-z\s]+:|\d+\.|Chapter|Section|Part)'
    
    chunks = re.split(heading_pattern, text)
    
    # Clean and filter chunks
    cleaned_chunks = []
    for chunk in chunks:
        chunk = chunk.strip()
        if chunk and len(chunk) > 10:  # Minimum chunk size
            cleaned_chunks.append(chunk)
    
    return cleaned_chunks if cleaned_chunks else [text]


def _chunk_semantic(text, embedder, similarity_threshold=0.5, max_chunk_size=500):
    """
    Semantic chunking based on sentence similarity.
    Groups sentences that are semantically similar together.
    
    Args:
        text: Input text to chunk
        embedder: Embedder instance for computing sentence embeddings
        similarity_threshold: Minimum cosine similarity to keep sentences together (0-1)
        max_chunk_size: Maximum chunk size in characters
        
    Returns:
        List of semantically coherent chunks
    """
    import numpy as np
    
    # Split into sentences
    if NLTK_AVAILABLE:
        try:
            sentences = nltk.sent_tokenize(text)
        except LookupError:
            try:
                nltk.download('punkt', quiet=True)
                sentences = nltk.sent_tokenize(text)
            except:
                sentences = re.split(r'[.!?]+', text)
    else:
        sentences = re.split(r'[.!?]+', text)
    
    # Clean sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= 1:
        return [text]
    
    # Encode sentences
    try:
        embeddings = embedder.encode(sentences, is_query=False)
    except TypeError:
        # Fallback for older embedder without is_query parameter
        embeddings = embedder.encode(sentences)
    
    # Compute cosine similarity helper
    def cosine_sim(a, b):
        """Compute cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)
    
    # Group sentences based on similarity
    chunks = []
    current_chunk = [sentences[0]]
    current_length = len(sentences[0])
    
    for i in range(1, len(sentences)):
        # Calculate similarity with previous sentence
        sim = cosine_sim(embeddings[i-1], embeddings[i])
        
        # Check if we should add to current chunk or start new one
        new_length = current_length + len(sentences[i]) + 1  # +1 for space
        
        if sim >= similarity_threshold and new_length <= max_chunk_size:
            # Add to current chunk
            current_chunk.append(sentences[i])
            current_length = new_length
        else:
            # Start new chunk
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentences[i]]
            current_length = len(sentences[i])
    
    # Add final chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks if chunks else [text]

