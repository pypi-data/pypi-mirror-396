"""Chunking strategies for RAG-TUI.

Provides multiple built-in chunking strategies and support for custom strategies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Callable, Optional
from enum import Enum
import re


class StrategyType(Enum):
    """Available chunking strategies."""
    TOKEN = "token"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    RECURSIVE = "recursive"
    FIXED_CHARS = "fixed_chars"
    CUSTOM = "custom"


@dataclass
class ChunkResult:
    """Result of chunking operation."""
    text: str
    start_pos: int
    end_pos: int
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ChunkingStrategy(ABC):
    """Base class for chunking strategies."""
    
    name: str = "base"
    description: str = "Base chunking strategy"
    
    @abstractmethod
    def chunk(self, text: str, chunk_size: int, overlap: int) -> List[ChunkResult]:
        """Split text into chunks.
        
        Args:
            text: The text to chunk
            chunk_size: Target size for chunks
            overlap: Amount of overlap between chunks
            
        Returns:
            List of ChunkResult objects
        """
        pass


class TokenStrategy(ChunkingStrategy):
    """Token-based chunking using Chonkie."""
    
    name = "token"
    description = "Split by token count (best for general text)"
    
    def __init__(self):
        self._chunker_cache = {}
    
    def _get_chunker(self, chunk_size: int, overlap: int):
        """Get or create a chunker with given params."""
        key = (chunk_size, overlap)
        if key not in self._chunker_cache:
            from chonkie import TokenChunker
            self._chunker_cache[key] = TokenChunker(
                chunk_size=chunk_size,
                chunk_overlap=overlap
            )
        return self._chunker_cache[key]
    
    def chunk(self, text: str, chunk_size: int, overlap: int) -> List[ChunkResult]:
        chunker = self._get_chunker(chunk_size, overlap)
        chunks = chunker.chunk(text)
        
        results = []
        for chunk in chunks:
            results.append(ChunkResult(
                text=chunk.text,
                start_pos=chunk.start_index,
                end_pos=chunk.end_index,
                metadata={"token_count": chunk.token_count}
            ))
        return results


class SentenceStrategy(ChunkingStrategy):
    """Sentence-based chunking - splits at sentence boundaries."""
    
    name = "sentence"
    description = "Split at sentence boundaries (best for natural language)"
    
    # Sentence ending patterns
    SENTENCE_ENDINGS = re.compile(r'(?<=[.!?])\s+')
    
    def chunk(self, text: str, chunk_size: int, overlap: int) -> List[ChunkResult]:
        # Split into sentences
        sentences = self.SENTENCE_ENDINGS.split(text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        results = []
        current_chunk = []
        current_length = 0
        chunk_start = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            # If adding this sentence exceeds chunk_size, save current chunk
            if current_length + sentence_len > chunk_size * 4 and current_chunk:  # ~4 chars per token
                chunk_text = ' '.join(current_chunk)
                results.append(ChunkResult(
                    text=chunk_text,
                    start_pos=chunk_start,
                    end_pos=chunk_start + len(chunk_text),
                    metadata={"sentence_count": len(current_chunk)}
                ))
                
                # Handle overlap by keeping last sentences
                overlap_chars = overlap * 4
                overlap_text = ""
                overlap_sentences = []
                for s in reversed(current_chunk):
                    if len(overlap_text) + len(s) < overlap_chars:
                        overlap_sentences.insert(0, s)
                        overlap_text = ' '.join(overlap_sentences)
                    else:
                        break
                
                chunk_start += len(chunk_text) - len(overlap_text)
                current_chunk = overlap_sentences
                current_length = len(overlap_text)
            
            current_chunk.append(sentence)
            current_length += sentence_len
        
        # Add remaining
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            results.append(ChunkResult(
                text=chunk_text,
                start_pos=chunk_start,
                end_pos=chunk_start + len(chunk_text),
                metadata={"sentence_count": len(current_chunk)}
            ))
        
        return results


class ParagraphStrategy(ChunkingStrategy):
    """Paragraph-based chunking - splits at double newlines."""
    
    name = "paragraph"
    description = "Split at paragraph breaks (best for structured documents)"
    
    def chunk(self, text: str, chunk_size: int, overlap: int) -> List[ChunkResult]:
        # Split by double newlines
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        results = []
        current_chunk = []
        current_length = 0
        chunk_start = 0
        
        for para in paragraphs:
            para_len = len(para)
            
            if current_length + para_len > chunk_size * 4 and current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                results.append(ChunkResult(
                    text=chunk_text,
                    start_pos=chunk_start,
                    end_pos=chunk_start + len(chunk_text),
                    metadata={"paragraph_count": len(current_chunk)}
                ))
                
                # Simple overlap: keep last paragraph if within overlap
                if len(current_chunk[-1]) < overlap * 4:
                    chunk_start += len(chunk_text) - len(current_chunk[-1])
                    current_chunk = [current_chunk[-1]]
                    current_length = len(current_chunk[0])
                else:
                    chunk_start += len(chunk_text)
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(para)
            current_length += para_len
        
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            results.append(ChunkResult(
                text=chunk_text,
                start_pos=chunk_start,
                end_pos=chunk_start + len(chunk_text),
                metadata={"paragraph_count": len(current_chunk)}
            ))
        
        return results


class RecursiveStrategy(ChunkingStrategy):
    """Recursive character splitting - tries multiple separators."""
    
    name = "recursive"
    description = "Try multiple separators recursively (best for code/mixed content)"
    
    SEPARATORS = ["\n\n", "\n", ". ", " ", ""]
    
    def chunk(self, text: str, chunk_size: int, overlap: int) -> List[ChunkResult]:
        target_size = chunk_size * 4  # chars
        
        def split_recursive(text: str, separators: List[str]) -> List[str]:
            if not separators:
                return [text]
            
            sep = separators[0]
            if not sep:
                # Final fallback: split by character
                return [text[i:i+target_size] for i in range(0, len(text), target_size - overlap * 4)]
            
            parts = text.split(sep)
            
            result = []
            current = []
            current_len = 0
            
            for part in parts:
                if current_len + len(part) > target_size and current:
                    result.append(sep.join(current))
                    current = []
                    current_len = 0
                
                if len(part) > target_size:
                    if current:
                        result.append(sep.join(current))
                        current = []
                        current_len = 0
                    result.extend(split_recursive(part, separators[1:]))
                else:
                    current.append(part)
                    current_len += len(part) + len(sep)
            
            if current:
                result.append(sep.join(current))
            
            return result
        
        chunks = split_recursive(text, self.SEPARATORS)
        
        results = []
        pos = 0
        for chunk_text in chunks:
            start = text.find(chunk_text, pos)
            if start == -1:
                start = pos
            results.append(ChunkResult(
                text=chunk_text,
                start_pos=start,
                end_pos=start + len(chunk_text),
                metadata={"method": "recursive"}
            ))
            pos = start + len(chunk_text)
        
        return results


class FixedCharsStrategy(ChunkingStrategy):
    """Fixed character count chunking."""
    
    name = "fixed_chars"
    description = "Split by fixed character count (simple, fast)"
    
    def chunk(self, text: str, chunk_size: int, overlap: int) -> List[ChunkResult]:
        char_size = chunk_size * 4  # Approximate chars per token
        char_overlap = overlap * 4
        
        results = []
        start = 0
        
        while start < len(text):
            end = min(start + char_size, len(text))
            chunk_text = text[start:end]
            
            results.append(ChunkResult(
                text=chunk_text,
                start_pos=start,
                end_pos=end,
                metadata={"char_count": len(chunk_text)}
            ))
            
            start = end - char_overlap
            if start >= len(text) - char_overlap:
                break
        
        return results


class CustomStrategy(ChunkingStrategy):
    """Custom user-defined chunking strategy."""
    
    name = "custom"
    description = "User-defined Python function"
    
    def __init__(self, chunk_fn: Optional[Callable] = None):
        """Initialize with a custom chunking function.
        
        Args:
            chunk_fn: Function with signature (text, chunk_size, overlap) -> List[Tuple[str, int, int]]
        """
        self._chunk_fn = chunk_fn
    
    def set_function(self, chunk_fn: Callable):
        """Set the custom chunking function."""
        self._chunk_fn = chunk_fn
    
    def chunk(self, text: str, chunk_size: int, overlap: int) -> List[ChunkResult]:
        if not self._chunk_fn:
            raise ValueError("Custom chunking function not set. Use set_function() first.")
        
        raw_chunks = self._chunk_fn(text, chunk_size, overlap)
        
        results = []
        for item in raw_chunks:
            if isinstance(item, tuple) and len(item) >= 3:
                chunk_text, start, end = item[:3]
                metadata = item[3] if len(item) > 3 else {}
            else:
                chunk_text = str(item)
                start = text.find(chunk_text)
                end = start + len(chunk_text)
                metadata = {}
            
            results.append(ChunkResult(
                text=chunk_text,
                start_pos=start,
                end_pos=end,
                metadata=metadata
            ))
        
        return results


# Strategy registry
STRATEGIES = {
    StrategyType.TOKEN: TokenStrategy,
    StrategyType.SENTENCE: SentenceStrategy,
    StrategyType.PARAGRAPH: ParagraphStrategy,
    StrategyType.RECURSIVE: RecursiveStrategy,
    StrategyType.FIXED_CHARS: FixedCharsStrategy,
    StrategyType.CUSTOM: CustomStrategy,
}


def get_strategy(strategy_type: StrategyType) -> ChunkingStrategy:
    """Get a chunking strategy instance.
    
    Args:
        strategy_type: The type of strategy to get
        
    Returns:
        An instance of the requested strategy
    """
    strategy_class = STRATEGIES.get(strategy_type)
    if not strategy_class:
        raise ValueError(f"Unknown strategy type: {strategy_type}")
    return strategy_class()


def get_strategy_info() -> List[dict]:
    """Get information about all available strategies.
    
    Returns:
        List of dicts with name, description for each strategy
    """
    info = []
    for strategy_type, strategy_class in STRATEGIES.items():
        info.append({
            "type": strategy_type,
            "name": strategy_class.name,
            "description": strategy_class.description
        })
    return info
