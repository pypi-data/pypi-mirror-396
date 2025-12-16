"""In-memory vector store using Usearch for similarity search."""

import numpy as np
from typing import List, Tuple, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from usearch.index import Index


class VectorStore:
    """Lightweight in-memory vector database for RAG operations."""
    
    def __init__(self, embedding_dim: int = 768):
        """Initialize the vector store.
        
        Args:
            embedding_dim: Dimensionality of the embeddings (default: 768 for nomic-embed-text)
        """
        self.embedding_dim = embedding_dim
        self.index = Index(ndim=embedding_dim, metric="cos")  # Cosine similarity
        self.chunks = []  # Store the original text chunks
        self.metadata = []  # Store metadata for each chunk
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._next_id = 0
    
    def add_chunks(
        self,
        chunks: List[str],
        embeddings: np.ndarray,
        metadata: Optional[List[dict]] = None
    ):
        """Add chunks with their embeddings to the vector store.
        
        Args:
            chunks: List of text chunks
            embeddings: NumPy array of embeddings (shape: [n_chunks, embedding_dim])
            metadata: Optional list of metadata dictionaries for each chunk
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        if metadata is None:
            metadata = [{} for _ in range(len(chunks))]
        
        # Add to the index
        for i, embedding in enumerate(embeddings):
            chunk_id = self._next_id
            self.index.add(chunk_id, embedding)
            self.chunks.append(chunks[i])
            self.metadata.append({
                **metadata[i],
                "chunk_id": chunk_id,
                "chunk_index": len(self.chunks) - 1
            })
            self._next_id += 1
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 3
    ) -> List[Tuple[str, float, dict]]:
        """Search for the most similar chunks to the query.
        
        Args:
            query_embedding: Query embedding vector (shape: [embedding_dim])
            top_k: Number of results to return (default: 3)
            
        Returns:
            List of tuples containing (chunk_text, similarity_score, metadata)
        """
        if len(self.chunks) == 0:
            return []
        
        # Perform similarity search
        matches = self.index.search(query_embedding, top_k)
        
        results = []
        for key, distance in zip(matches.keys, matches.distances):
            # Convert distance to similarity score (cosine distance -> similarity)
            similarity = 1 - distance
            
            # Find the chunk by ID
            chunk_idx = None
            for idx, meta in enumerate(self.metadata):
                if meta["chunk_id"] == key:
                    chunk_idx = idx
                    break
            
            if chunk_idx is not None:
                results.append((
                    self.chunks[chunk_idx],
                    float(similarity),
                    self.metadata[chunk_idx].copy()
                ))
        
        return results
    
    async def search_async(
        self,
        query_embedding: np.ndarray,
        top_k: int = 3
    ) -> List[Tuple[str, float, dict]]:
        """Asynchronously search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector (shape: [embedding_dim])
            top_k: Number of results to return (default: 3)
            
        Returns:
            List of tuples containing (chunk_text, similarity_score, metadata)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self.search,
            query_embedding,
            top_k
        )
    
    def clear(self):
        """Clear all chunks and reset the index."""
        self.index = Index(ndim=self.embedding_dim, metric="cos")
        self.chunks = []
        self.metadata = []
        self._next_id = 0
    
    def get_stats(self) -> dict:
        """Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
        """
        return {
            "total_chunks": len(self.chunks),
            "embedding_dim": self.embedding_dim,
            "index_size": self.index.size,
            "memory_usage_mb": self.index.memory_usage / (1024 * 1024)
        }
    
    def count(self) -> int:
        """Return the number of chunks in the store."""
        return len(self.chunks)
    
    def shutdown(self):
        """Cleanup resources."""
        self._executor.shutdown(wait=True)


class EmbeddingCache:
    """Cache for embeddings to avoid recomputing."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize the cache.
        
        Args:
            max_size: Maximum number of embeddings to cache
        """
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
    
    def get(self, text: str) -> Optional[np.ndarray]:
        """Get cached embedding for text.
        
        Args:
            text: The text to lookup
            
        Returns:
            Cached embedding or None if not found
        """
        if text in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(text)
            self.access_order.append(text)
            return self.cache[text]
        return None
    
    def put(self, text: str, embedding: np.ndarray):
        """Cache an embedding.
        
        Args:
            text: The text key
            embedding: The embedding vector
        """
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size and text not in self.cache:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[text] = embedding
        if text in self.access_order:
            self.access_order.remove(text)
        self.access_order.append(text)
    
    def clear(self):
        """Clear the cache."""
        self.cache = {}
        self.access_order = []
