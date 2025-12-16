"""Metrics and batch testing for RAG-TUI."""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import json
from datetime import datetime


@dataclass
class QueryResult:
    """Result of a single query."""
    query: str
    chunks_retrieved: List[Tuple[str, float]]  # (chunk_text, score)
    top_score: float
    avg_score: float
    response: Optional[str] = None


@dataclass
class BatchTestResult:
    """Results of batch testing."""
    queries: List[QueryResult]
    timestamp: str
    total_queries: int
    avg_top_score: float
    avg_retrieval_score: float
    hit_rate: float  # % of queries with score > threshold
    
    def to_dict(self) -> dict:
        """Convert to dictionary for export."""
        return {
            "timestamp": self.timestamp,
            "total_queries": self.total_queries,
            "avg_top_score": round(self.avg_top_score, 4),
            "avg_retrieval_score": round(self.avg_retrieval_score, 4),
            "hit_rate": round(self.hit_rate, 4),
            "queries": [
                {
                    "query": q.query,
                    "top_score": round(q.top_score, 4),
                    "avg_score": round(q.avg_score, 4),
                    "chunks_count": len(q.chunks_retrieved)
                }
                for q in self.queries
            ]
        }


@dataclass
class ChunkConfig:
    """Chunking configuration for export."""
    strategy: str
    chunk_size: int
    overlap_percent: int
    overlap_tokens: int
    
    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy,
            "chunk_size": self.chunk_size,
            "overlap_percent": self.overlap_percent,
            "overlap_tokens": self.overlap_tokens
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def to_langchain(self) -> str:
        """Generate LangChain-compatible config."""
        return f'''from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size={self.chunk_size * 4},  # ~{self.chunk_size} tokens
    chunk_overlap={self.overlap_tokens * 4},
    length_function=len,
)
'''
    
    def to_llamaindex(self) -> str:
        """Generate LlamaIndex-compatible config."""
        return f'''from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(
    chunk_size={self.chunk_size * 4},
    chunk_overlap={self.overlap_tokens * 4},
)
'''
    
    @classmethod
    def from_dict(cls, data: dict) -> "ChunkConfig":
        return cls(
            strategy=data.get("strategy", "token"),
            chunk_size=data.get("chunk_size", 200),
            overlap_percent=data.get("overlap_percent", 10),
            overlap_tokens=data.get("overlap_tokens", 20)
        )


def calculate_batch_metrics(results: List[QueryResult], threshold: float = 0.5) -> BatchTestResult:
    """Calculate metrics from batch query results.
    
    Args:
        results: List of QueryResult objects
        threshold: Score threshold for counting as a "hit"
        
    Returns:
        BatchTestResult with aggregate metrics
    """
    if not results:
        return BatchTestResult(
            queries=[],
            timestamp=datetime.now().isoformat(),
            total_queries=0,
            avg_top_score=0.0,
            avg_retrieval_score=0.0,
            hit_rate=0.0
        )
    
    total_top_score = sum(r.top_score for r in results)
    total_avg_score = sum(r.avg_score for r in results)
    hits = sum(1 for r in results if r.top_score >= threshold)
    
    return BatchTestResult(
        queries=results,
        timestamp=datetime.now().isoformat(),
        total_queries=len(results),
        avg_top_score=total_top_score / len(results),
        avg_retrieval_score=total_avg_score / len(results),
        hit_rate=hits / len(results)
    )


def export_config(config: ChunkConfig, format: str = "json") -> str:
    """Export configuration in specified format.
    
    Args:
        config: The chunk configuration
        format: One of "json", "langchain", "llamaindex"
        
    Returns:
        Configuration string
    """
    if format == "json":
        return config.to_json()
    elif format == "langchain":
        return config.to_langchain()
    elif format == "llamaindex":
        return config.to_llamaindex()
    else:
        raise ValueError(f"Unknown format: {format}")
