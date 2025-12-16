"""Bottom control bar with chunk parameters."""

from textual.widgets import Static, Input, Label
from textual.containers import Horizontal, Container
from textual.app import ComposeResult
from textual.message import Message


class ControlBar(Container):
    """Bottom control bar for chunk size and overlap settings."""
    
    DEFAULT_CSS = """
    ControlBar {
        dock: bottom;
        height: auto;
        padding: 1 2;
        background: $surface-darken-1;
        border-top: solid $primary;
    }
    
    ControlBar Horizontal {
        height: auto;
        align: center middle;
    }
    
    ControlBar .control-group {
        width: auto;
        margin-right: 3;
    }
    
    ControlBar Label {
        margin-right: 1;
        color: $text;
    }
    
    ControlBar Input {
        width: 8;
        text-align: center;
    }
    
    ControlBar .status {
        dock: right;
        color: $success;
        text-style: bold;
    }
    """
    
    class ParametersChanged(Message):
        """Message sent when chunk parameters change."""
        
        def __init__(self, chunk_size: int, overlap_percent: int):
            self.chunk_size = chunk_size
            self.overlap_percent = overlap_percent
            super().__init__()
    
    def __init__(self, chunk_size: int = 200, overlap_percent: int = 10, **kwargs):
        """Initialize the control bar.
        
        Args:
            chunk_size: Default chunk size in tokens
            overlap_percent: Default overlap percentage
        """
        super().__init__(**kwargs)
        self._chunk_size = chunk_size
        self._overlap_percent = overlap_percent
        self._status = "Ready"
    
    def compose(self) -> ComposeResult:
        """Compose the control bar."""
        with Horizontal():
            # Chunk size control
            with Horizontal(classes="control-group"):
                yield Label("📏 Chunk Size:")
                yield Input(
                    str(self._chunk_size),
                    type="integer",
                    id="chunk-size-input",
                    placeholder="200"
                )
                yield Label("tokens")
            
            # Overlap control
            with Horizontal(classes="control-group"):
                yield Label("🔗 Overlap:")
                yield Input(
                    str(self._overlap_percent),
                    type="integer",
                    id="overlap-input",
                    placeholder="10"
                )
                yield Label("%")
            
            # Status indicator
            yield Static(f"⚡ {self._status}", classes="status", id="status-display")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        try:
            if event.input.id == "chunk-size-input":
                value = int(event.value) if event.value else 200
                self._chunk_size = max(50, min(2000, value))
            elif event.input.id == "overlap-input":
                value = int(event.value) if event.value else 10
                self._overlap_percent = max(0, min(50, value))
            
            self.post_message(self.ParametersChanged(
                self._chunk_size,
                self._overlap_percent
            ))
        except ValueError:
            pass  # Ignore invalid input
    
    def update_status(self, status: str) -> None:
        """Update the status display.
        
        Args:
            status: New status text
        """
        self._status = status
        status_display = self.query_one("#status-display", Static)
        status_display.update(f"⚡ {status}")
    
    @property
    def chunk_size(self) -> int:
        """Get current chunk size."""
        return self._chunk_size
    
    @property
    def overlap_percent(self) -> int:
        """Get current overlap percentage."""
        return self._overlap_percent
