import customtkinter as ctk

class HeaderComponent(ctk.CTkFrame):
    """Header component with logo and title."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the header UI elements."""
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(side="left")
        
        self.logo_label = ctk.CTkLabel(
            self.logo_frame, 
            text="▶", 
            font=("Arial", 28),
            text_color="#4d90fe"
        )
        self.logo_label.pack(side="left", padx=5)
        
        self.title_label = ctk.CTkLabel(
            self.logo_frame, 
            text="YouTube Downloader Pro",
            font=("Arial", 24, "bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(side="left")