import customtkinter as ctk

class URLInputComponent(ctk.CTkFrame):
    """URL input component with validation."""
    
    def __init__(self, parent, on_url_change_callback):
        super().__init__(parent, fg_color="#252525", corner_radius=10)
        self.on_url_change_callback = on_url_change_callback
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the URL input UI elements."""
        self.url_label = ctk.CTkLabel(
            self, 
            text="YouTube URL:",
            font=("Arial", 14),
            text_color="#cccccc"
        )
        self.url_label.pack(side="left", padx=(15, 10), pady=15)
        
        self.url_entry = ctk.CTkEntry(
            self, 
            width=600,
            height=40,
            placeholder_text="Paste video or playlist URL here...",
            fg_color="#333333",
            border_color="#4d90fe",
            text_color="#ffffff",
            placeholder_text_color="#999999"
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=15)
        self.url_entry.bind('<KeyRelease>', self._on_url_change)
        self.url_entry.bind('<FocusOut>', self._on_url_change)
    
    def _on_url_change(self, event=None):
        """Handle URL input changes."""
        if self.on_url_change_callback:
            self.on_url_change_callback(self.url_entry.get().strip())
    
    def get_url(self):
        """Get the current URL from the entry."""
        return self.url_entry.get().strip()
    
    def set_state(self, state):
        """Set the state of the URL entry."""
        self.url_entry.configure(state=state)