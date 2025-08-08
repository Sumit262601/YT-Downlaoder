import customtkinter as ctk
import threading

class URLInputComponent(ctk.CTkFrame):
    """URL input component with validation."""
    
    def __init__(self, parent, on_url_change_callback):
        super().__init__(parent, fg_color="#252525", corner_radius=10)
        self.on_url_change_callback = on_url_change_callback
        self._current_url = ""  # Track current URL to prevent duplicate requests
        self._debounce_timer = None  # For debouncing URL changes
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
        
        # Add URL type indicator
        self.url_type_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 10),
            text_color="#888888"
        )
        self.url_type_label.pack(side="right", padx=(0, 15))
    
    def _on_url_change(self, event=None):
        """Handle URL input changes with debouncing."""
        # Cancel previous timer if it exists
        if self._debounce_timer:
            self._debounce_timer.cancel()
        
        # Start new timer for debouncing (wait 500ms after user stops typing)
        self._debounce_timer = threading.Timer(0.5, self._process_url_change)
        self._debounce_timer.start()
    
    def _process_url_change(self):
        """Process URL change after debouncing."""
        url = self.url_entry.get().strip()
        
        # Don't process if URL hasn't actually changed
        if url == self._current_url:
            return
        
        self._current_url = url
        
        # Update UI in main thread
        if hasattr(self, 'master') and hasattr(self.master, 'after'):
            self.master.after(0, lambda: self._update_url_type_indicator(url))
        
        # Trigger callback if provided
        if self.on_url_change_callback:
            self.on_url_change_callback(url)
    
    def _update_url_type_indicator(self, url):
        """Update the URL type indicator."""
        if not url:
            self.url_type_label.configure(text="")
        elif not self._validate_basic_url(url):
            self.url_type_label.configure(text="❌ Invalid URL", text_color="#ff4444")
        elif self._is_playlist_url(url):
            self.url_type_label.configure(text="📋 Playlist", text_color="#44ff44")
        elif self._is_single_video_url(url):
            self.url_type_label.configure(text="🎥 Single Video", text_color="#44ff44")
        else:
            self.url_type_label.configure(text="❓ Unknown", text_color="#ffaa44")
    
    def _validate_basic_url(self, url):
        """Basic URL validation."""
        return "youtube.com" in url.lower() or "youtu.be" in url.lower()
    
    def _is_playlist_url(self, url):
        """Check if URL is a playlist."""
        from utils.validators import URLValidator
        return URLValidator.is_playlist(url)
    
    def _is_single_video_url(self, url):
        """Check if URL is a single video."""
        from utils.validators import URLValidator
        return URLValidator.is_single_video(url)
    
    def get_url(self):
        """Get the current URL from the entry."""
        return self.url_entry.get().strip()
    
    def set_state(self, state):
        """Set the state of the URL entry."""
        self.url_entry.configure(state=state)