import customtkinter as ctk

class FooterComponent(ctk.CTkFrame):
    """Footer component with application information."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the footer UI elements."""
        self.publisher_label = ctk.CTkLabel(
            self,
            text="© 2025 YouTube Downloader Pro | v2.0",
            font=("Arial", 10),
            text_color="#666666"
        )
        self.publisher_label.pack()