"""Preset management for RAG-TUI."""

import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


# Default presets directory
PRESETS_DIR = Path.home() / ".rag-tui" / "presets"


@dataclass
class Preset:
    """A saved chunking configuration preset."""
    name: str
    strategy: str
    chunk_size: int
    overlap_percent: int
    description: str = ""
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# Built-in presets - based on industry research and best practices
BUILTIN_PRESETS = [
    Preset(
        name="📄 General Text",
        strategy="token",
        chunk_size=256,
        overlap_percent=10,
        description="Balanced default for most documents (256 tokens, 10% overlap)"
    ),
    Preset(
        name="💬 Q&A / FAQ",
        strategy="token",
        chunk_size=128,
        overlap_percent=15,
        description="Small precise chunks for fact-based questions"
    ),
    Preset(
        name="📚 Long Documents",
        strategy="paragraph",
        chunk_size=512,
        overlap_percent=10,
        description="Larger chunks for context-heavy documents"
    ),
    Preset(
        name="💻 Code Files",
        strategy="recursive",
        chunk_size=400,
        overlap_percent=20,
        description="Recursive splitting respects code structure"
    ),
    Preset(
        name="⚖️ Legal/Technical",
        strategy="sentence",
        chunk_size=300,
        overlap_percent=25,
        description="Higher overlap preserves cross-references"
    ),
    Preset(
        name="🎯 High Precision",
        strategy="token",
        chunk_size=100,
        overlap_percent=30,
        description="Very small chunks for exact matching"
    ),
    Preset(
        name="📝 Summarization",
        strategy="paragraph",
        chunk_size=800,
        overlap_percent=5,
        description="Large chunks maintain narrative flow"
    ),
    Preset(
        name="💬 Chat/Support",
        strategy="sentence",
        chunk_size=150,
        overlap_percent=20,
        description="Conversational context preservation"
    ),
]


def ensure_presets_dir() -> Path:
    """Ensure the presets directory exists."""
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    return PRESETS_DIR


def save_preset(preset: Preset) -> str:
    """Save a preset to disk.
    
    Args:
        preset: The preset to save
        
    Returns:
        Path to saved file
    """
    ensure_presets_dir()
    
    # Sanitize name for filename
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in preset.name)
    file_path = PRESETS_DIR / f"{safe_name}.json"
    
    with open(file_path, 'w') as f:
        json.dump(asdict(preset), f, indent=2)
    
    return str(file_path)


def load_preset(name: str) -> Optional[Preset]:
    """Load a preset by name.
    
    Args:
        name: Name of the preset
        
    Returns:
        Preset object or None if not found
    """
    # Check built-in first
    for preset in BUILTIN_PRESETS:
        if preset.name.lower() == name.lower():
            return preset
    
    # Check saved presets
    ensure_presets_dir()
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    file_path = PRESETS_DIR / f"{safe_name}.json"
    
    if file_path.exists():
        with open(file_path, 'r') as f:
            data = json.load(f)
            return Preset(**data)
    
    return None


def list_presets() -> List[Preset]:
    """List all available presets (built-in + saved).
    
    Returns:
        List of Preset objects
    """
    presets = list(BUILTIN_PRESETS)
    
    ensure_presets_dir()
    
    for file_path in PRESETS_DIR.glob("*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                preset = Preset(**data)
                # Don't duplicate built-ins
                if not any(p.name == preset.name for p in presets):
                    presets.append(preset)
        except Exception:
            continue  # Skip invalid files
    
    return presets


def delete_preset(name: str) -> bool:
    """Delete a saved preset.
    
    Args:
        name: Name of the preset
        
    Returns:
        True if deleted, False if not found or built-in
    """
    # Can't delete built-ins
    if any(p.name.lower() == name.lower() for p in BUILTIN_PRESETS):
        return False
    
    ensure_presets_dir()
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    file_path = PRESETS_DIR / f"{safe_name}.json"
    
    if file_path.exists():
        file_path.unlink()
        return True
    
    return False
