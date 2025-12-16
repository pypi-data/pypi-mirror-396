"""Search panel with query input and similarity results."""

from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.app import ComposeResult
from textual.message import Message
from rich.text import Text
from typing import List, Tuple


class SimilarityBar(Static):
    """Visual similarity score display."""
    
    DEFAULT_CSS = """
    SimilarityBar {
        height: 1;
        width: 100%;
    }
    """
    
    def __init__(self, score: float, **kwargs):
        """Initialize similarity bar.
        
        Args:
            score: Similarity score between 0 and 1
        """
        super().__init__(**kwargs)
        self.score = score
    
    def on_mount(self) -> None:
        """Render the bar on mount."""
        self._render_bar()
    
    def _render_bar(self) -> None:
        """Render the similarity bar."""
        # Calculate fill
        width = 30
        filled = int(width * self.score)
        empty = width - filled
        
        # Color based on score
        if self.score >= 0.8:
            color = "green"
        elif self.score >= 0.5:
            color = "yellow"
        else:
            color = "red"
        
        bar = Text()
        bar.append("│", style="dim")
        bar.append("█" * filled, style=color)
        bar.append("░" * empty, style="dim")
        bar.append("│", style="dim")
        bar.append(f" {self.score:.3f}", style=f"bold {color}")
        
        self.update(bar)


class ResultCard(Static):
    """A card displaying a single search result."""
    
    DEFAULT_CSS = """
    ResultCard {
        height: auto;
        margin: 1 0;
        padding: 1 2;
        border: solid $accent;
        background: $surface;
    }
    
    ResultCard .result-rank {
        color: $warning;
        text-style: bold;
    }
    
    ResultCard .result-content {
        margin-top: 1;
        color: $text;
    }
    """
    
    def __init__(
        self,
        rank: int,
        chunk_text: str,
        score: float,
        **kwargs
    ):
        """Initialize result card.
        
        Args:
            rank: Result rank (1-based)
            chunk_text: The chunk text
            score: Similarity score
        """
        super().__init__(**kwargs)
        self.rank = rank
        self.chunk_text = chunk_text
        self.score = score
    
    def compose(self) -> ComposeResult:
        """Compose the result card."""
        # Rank header
        yield Static(f"🏆 #{self.rank}", classes="result-rank")
        
        # Similarity bar
        yield SimilarityBar(self.score)
        
        # Content preview
        preview = self.chunk_text[:300]
        if len(self.chunk_text) > 300:
            preview += "..."
        yield Static(preview, classes="result-content")


class SearchPanel(Vertical):
    """Panel for query input and search results."""
    
    DEFAULT_CSS = """
    SearchPanel {
        height: 1fr;
        padding: 1;
    }
    
    SearchPanel .query-section {
        height: auto;
        padding: 1;
        border: solid $primary;
        margin-bottom: 1;
    }
    
    SearchPanel .query-row {
        height: auto;
    }
    
    SearchPanel Input {
        width: 1fr;
    }
    
    SearchPanel Button {
        margin-left: 1;
    }
    
    SearchPanel .results-section {
        height: 1fr;
        overflow-y: auto;
    }
    
    SearchPanel .empty-results {
        color: $text-muted;
        text-align: center;
        padding: 4;
    }
    """
    
    class QuerySubmitted(Message):
        """Message when query is submitted."""
        
        def __init__(self, query: str, action: str):
            self.query = query
            self.action = action  # "search" or "generate"
            super().__init__()
    
    def __init__(self, **kwargs):
        """Initialize the search panel."""
        super().__init__(**kwargs)
        self._results = []
    
    def compose(self) -> ComposeResult:
        """Compose the search panel."""
        # Query section
        with Vertical(classes="query-section"):
            yield Static("🔍 Search & Generate", classes="section-title")
            with Horizontal(classes="query-row"):
                yield Input(
                    placeholder="Ask a question about the text...",
                    id="query-input"
                )
                yield Button("Search", variant="primary", id="search-btn")
                yield Button("Generate", variant="success", id="generate-btn")
        
        # Results section
        with VerticalScroll(classes="results-section", id="results-container"):
            yield Static("💡 Enter a query and click Search to find relevant chunks.", classes="empty-results")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        query_input = self.query_one("#query-input", Input)
        query = query_input.value.strip()
        
        if query:
            action = "search" if event.button.id == "search-btn" else "generate"
            self.post_message(self.QuerySubmitted(query, action))
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in query input."""
        if event.input.id == "query-input" and event.value.strip():
            self.post_message(self.QuerySubmitted(event.value.strip(), "search"))
    
    def update_results(self, results: List[Tuple[str, float, dict]]) -> None:
        """Update search results.
        
        Args:
            results: List of (chunk_text, score, metadata) tuples
        """
        self._results = results
        container = self.query_one("#results-container", VerticalScroll)
        container.remove_children()
        
        if not results:
            container.mount(Static("No matching chunks found.", classes="empty-results"))
            return
        
        for i, (chunk_text, score, _) in enumerate(results, 1):
            card = ResultCard(rank=i, chunk_text=chunk_text, score=score)
            container.mount(card)
    
    @property
    def current_query(self) -> str:
        """Get the current query text."""
        return self.query_one("#query-input", Input).value
