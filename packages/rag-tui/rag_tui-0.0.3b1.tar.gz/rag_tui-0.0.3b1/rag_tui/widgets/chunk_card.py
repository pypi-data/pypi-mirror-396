"""Chunk card widget for displaying individual chunks with colors."""

from textual.widgets import Static
from textual.containers import Vertical, Container, VerticalScroll
from textual.app import ComposeResult


# Beautiful color palette for chunk borders and backgrounds
CHUNK_COLORS = [
    ("#3b82f6", "#1e3a5f"),  # Blue
    ("#22c55e", "#166534"),  # Green  
    ("#a855f7", "#581c87"),  # Purple
    ("#f97316", "#9a3412"),  # Orange
    ("#06b6d4", "#155e75"),  # Cyan
    ("#ec4899", "#831843"),  # Pink
]


class ChunkCard(Container):
    """A styled card displaying a single chunk with colored border."""
    
    DEFAULT_CSS = """
    ChunkCard {
        height: auto;
        max-height: 20;
        margin: 1 0;
        padding: 1 2;
        border: solid $primary;
        background: $surface;
    }
    
    ChunkCard > Static {
        height: auto;
    }
    
    ChunkCard .chunk-header {
        text-style: bold;
        margin-bottom: 1;
    }
    
    ChunkCard .chunk-header-row {
        height: auto;
        margin-bottom: 1;
        width: 100%;
    }
    
    ChunkCard .chunk-header {
        width: 1fr;
    }
    
    ChunkCard .copy-btn {
        min-width: 8;
        height: 3;
        margin-left: 1;
        background: $success;
        color: $text;
    }
    
    ChunkCard .chunk-scroll {
        height: auto;
        max-height: 12;
        overflow-y: auto;
        padding: 0 1;
        margin-bottom: 1;
    }
    
    ChunkCard .chunk-content {
        height: auto;
    }
    
    ChunkCard .chunk-meta {
        color: $text-muted;
        text-style: italic;
    }
    
    ChunkCard .overlap-indicator {
        color: #fbbf24;
        text-style: bold;
    }
    """
    
    def __init__(
        self,
        chunk_text: str,
        chunk_index: int,
        start_pos: int,
        end_pos: int,
        token_count: int = 0,
        overlap_text: str = "",
        **kwargs
    ):
        """Initialize the chunk card.
        
        Args:
            chunk_text: The text content of the chunk
            chunk_index: Index of this chunk (0-based)
            start_pos: Starting character position in original text
            end_pos: Ending character position in original text
            token_count: Estimated token count
            overlap_text: Text that overlaps with next chunk (for visualization)
        """
        super().__init__(**kwargs)
        self.chunk_text = chunk_text
        self.chunk_index = chunk_index
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.token_count = token_count
        self.overlap_text = overlap_text
        
        # Get color for this chunk
        color_idx = chunk_index % len(CHUNK_COLORS)
        self.border_color, self.bg_color = CHUNK_COLORS[color_idx]
    
    def _get_quality_indicators(self) -> str:
        """Analyze chunk quality and return indicators."""
        indicators = []
        text = self.chunk_text.strip()
        
        # Check if ends with sentence terminator
        if text and text[-1] in '.!?':
            indicators.append("🟢")
        elif text and text[-1] in ',:;':
            indicators.append("🟡")  # Ends mid-phrase
        else:
            indicators.append("🔴")  # Cut off
        
        # Check length
        if self.token_count < 50:
            indicators.append("⚠️SHORT")
        elif self.token_count > 600:
            indicators.append("⚠️LONG")
        
        # Check if starts with lowercase (likely mid-sentence)
        if text and text[0].islower():
            indicators.append("↪️CUT")
        
        return " ".join(indicators) if indicators else "🟢"
    
    def _format_content_with_overlap(self) -> str:
        """Format chunk content with overlap highlighting using Rich markup."""
        if not self.overlap_text or self.overlap_text not in self.chunk_text:
            return self.chunk_text
        
        # Find where the overlap text appears (should be at the end)
        overlap_start = self.chunk_text.rfind(self.overlap_text)
        if overlap_start == -1:
            return self.chunk_text
        
        # Split text and highlight overlap
        before = self.chunk_text[:overlap_start]
        overlap = self.chunk_text[overlap_start:]
        
        # Use Rich markup for highlighting
        return f"{before}[bold yellow on #4a3f00]{overlap}[/]"
    
    def on_mount(self) -> None:
        """Apply dynamic styling on mount."""
        self.styles.border = ("solid", self.border_color)
        self.styles.background = self.bg_color
    
    async def on_button_pressed(self, event) -> None:
        """Handle copy button press."""
        if hasattr(event.button, 'id') and event.button.id and event.button.id.startswith("copy-"):
            try:
                import pyperclip
                pyperclip.copy(self.chunk_text)
                self.app.notify("📋 Chunk copied to clipboard!", timeout=2)
            except ImportError:
                # Fallback: try using pbcopy on macOS
                try:
                    import subprocess
                    subprocess.run(['pbcopy'], input=self.chunk_text.encode(), check=True)
                    self.app.notify("📋 Chunk copied to clipboard!", timeout=2)
                except Exception:
                    self.app.notify("⚠️ Install pyperclip for clipboard support", severity="warning")
            except Exception as e:
                self.app.notify(f"Copy failed: {e}", severity="warning")
    
    def compose(self) -> ComposeResult:
        """Compose the chunk card content."""
        from textual.widgets import Button
        from textual.containers import Horizontal
        
        # Header with quality indicator and copy button
        quality = self._get_quality_indicators()
        overlap_indicator = " 🔗" if self.overlap_text else ""
        header_text = f"█ Chunk {self.chunk_index + 1}  │  {len(self.chunk_text)} chars  │  ~{self.token_count} tok  │  {quality}{overlap_indicator}"
        
        with Horizontal(classes="chunk-header-row"):
            yield Static(header_text, classes="chunk-header")
            yield Button("Copy", id=f"copy-{self.chunk_index}", classes="copy-btn", variant="success")
        
        # Full content in scrollable container with overlap highlighting
        with VerticalScroll(classes="chunk-scroll"):
            content = self._format_content_with_overlap()
            yield Static(content, classes="chunk-content", markup=True)
        
        # Metadata with overlap info
        meta_parts = [f"📍 Position: {self.start_pos} → {self.end_pos}"]
        if self.overlap_text:
            meta_parts.append(f"🔗 Overlap: {len(self.overlap_text)} chars")
        yield Static("  │  ".join(meta_parts), classes="chunk-meta")


class ChunkList(Vertical):
    """Container for displaying multiple chunk cards."""
    
    DEFAULT_CSS = """
    ChunkList {
        height: 1fr;
        padding: 1;
        overflow-y: auto;
    }
    
    ChunkList .empty-state {
        color: $text-muted;
        text-align: center;
        padding: 4;
    }
    """
    
    def __init__(self, **kwargs):
        """Initialize the chunk list."""
        super().__init__(**kwargs)
        self._chunks = []
    
    def update_chunks(self, chunks: list) -> None:
        """Update the displayed chunks."""
        self._chunks = chunks
        self._rebuild_cards()
    
    def _rebuild_cards(self) -> None:
        """Rebuild all chunk cards with overlap detection."""
        self.remove_children()
        
        if not self._chunks:
            self.mount(Static("📭 No chunks yet. Load text to begin.", classes="empty-state"))
            return
        
        for i, (text, start, end) in enumerate(self._chunks):
            token_estimate = len(text) // 4
            
            # Calculate overlap with next chunk
            overlap_text = ""
            if i < len(self._chunks) - 1:
                next_text, next_start, next_end = self._chunks[i + 1]
                # If next chunk starts before this one ends, there's overlap
                if next_start < end:
                    overlap_len = end - next_start
                    # Get the overlapping portion from end of current chunk
                    overlap_text = text[-overlap_len:] if overlap_len <= len(text) else ""
            
            card = ChunkCard(
                chunk_text=text,
                chunk_index=i,
                start_pos=start,
                end_pos=end,
                token_count=token_estimate,
                overlap_text=overlap_text,
                id=f"chunk-{i}"
            )
            self.mount(card)
