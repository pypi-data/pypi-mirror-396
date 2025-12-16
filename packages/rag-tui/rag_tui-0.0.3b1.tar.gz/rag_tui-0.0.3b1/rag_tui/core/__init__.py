"""RAG-TUI Core - Chunking Engine, Strategies, and Utilities."""

from rag_tui.core.engine import ChunkingEngine
from rag_tui.core.strategies import (
    StrategyType,
    ChunkingStrategy,
    TokenStrategy,
    SentenceStrategy,
    ParagraphStrategy,
    RecursiveStrategy,
    FixedCharsStrategy,
    CustomStrategy,
    get_strategy,
    get_strategy_info,
    STRATEGIES,
)
from rag_tui.core.vector import VectorStore, EmbeddingCache
from rag_tui.core.llm import OllamaLLM
from rag_tui.core.file_handler import read_file, FileInfo, SUPPORTED_EXTENSIONS
from rag_tui.core.metrics import ChunkConfig, QueryResult, BatchTestResult, calculate_batch_metrics

__all__ = [
    # Engine
    "ChunkingEngine",
    # Strategies
    "StrategyType",
    "ChunkingStrategy",
    "TokenStrategy",
    "SentenceStrategy",
    "ParagraphStrategy",
    "RecursiveStrategy",
    "FixedCharsStrategy",
    "CustomStrategy",
    "get_strategy",
    "get_strategy_info",
    "STRATEGIES",
    # Vector
    "VectorStore",
    "EmbeddingCache",
    # LLM
    "OllamaLLM",
    # File
    "read_file",
    "FileInfo",
    "SUPPORTED_EXTENSIONS",
    # Metrics
    "ChunkConfig",
    "QueryResult",
    "BatchTestResult",
    "calculate_batch_metrics",
]
