"""File handling utilities for RAG-TUI with PDF support."""

from pathlib import Path
from typing import Tuple
from dataclasses import dataclass


@dataclass
class FileInfo:
    """Information about a loaded file."""
    path: str
    name: str
    extension: str
    size_bytes: int
    line_count: int
    char_count: int
    encoding: str = "utf-8"
    page_count: int = 0  # For PDFs


SUPPORTED_EXTENSIONS = {
    ".txt": "Plain text",
    ".md": "Markdown",
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".xml": "XML",
    ".html": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
    ".sh": "Shell",
    ".rst": "reStructuredText",
    ".tex": "LaTeX",
    ".csv": "CSV",
    ".pdf": "PDF Document",
}


def read_pdf(file_path: str) -> Tuple[str, int]:
    """Read text content from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple of (extracted_text, page_count)
    """
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(file_path)
        pages = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages.append(f"--- Page {i+1} ---\n{text}")
        
        return "\n\n".join(pages), len(reader.pages)
    except ImportError:
        raise ImportError("pypdf is required for PDF support. Install with: pip install pypdf")
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {e}")


def read_file(file_path: str) -> Tuple[str, FileInfo]:
    """Read a file and return its contents and info.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (content, FileInfo)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type not supported
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS.keys())}")
    
    # Handle PDFs separately
    if ext == ".pdf":
        content, page_count = read_pdf(file_path)
        info = FileInfo(
            path=str(path.absolute()),
            name=path.name,
            extension=ext,
            size_bytes=path.stat().st_size,
            line_count=content.count('\n') + 1,
            char_count=len(content),
            encoding="pdf",
            page_count=page_count
        )
        return content, info
    
    # Handle text files
    content = None
    encoding = "utf-8"
    
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            with open(path, "r", encoding=enc) as f:
                content = f.read()
            encoding = enc
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        raise ValueError(f"Could not decode file: {file_path}")
    
    info = FileInfo(
        path=str(path.absolute()),
        name=path.name,
        extension=ext,
        size_bytes=path.stat().st_size,
        line_count=content.count('\n') + 1,
        char_count=len(content),
        encoding=encoding
    )
    
    return content, info


def get_file_preview(content: str, max_lines: int = 10) -> str:
    """Get a preview of file content."""
    lines = content.split('\n')[:max_lines]
    preview = '\n'.join(lines)
    
    if len(content.split('\n')) > max_lines:
        preview += f"\n... ({len(content.split(chr(10))) - max_lines} more lines)"
    
    return preview


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
