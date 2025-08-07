import customtkinter as ctk

class ProgressComponent(ctk.CTkFrame):
    """Progress component showing download progress and status."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="#252525", corner_radius=10)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the progress UI elements."""
        self.progress_top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_top_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        self.progress_label = ctk.CTkLabel(
            self.progress_top_frame,
            text="Download Progress:",
            font=("Arial", 14),
            text_color="#cccccc"
        )
        self.progress_label.pack(side="left")
        
        self.percentage_label = ctk.CTkLabel(
            self.progress_top_frame,
            text="0%",
            font=("Arial", 14, "bold"),
            text_color="#4d90fe"
        )
        self.percentage_label.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=400,
            height=8,
            progress_color="#4d90fe"
        )
        self.progress_bar.pack(pady=(0, 15))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready to download",
            font=("Arial", 12),
            text_color="#aaaaaa"
        )
        self.status_label.pack(pady=(0, 15))
    
    def update_progress(self, percentage):
        """Update the progress bar and percentage."""
        self.progress_bar.set(percentage)
        self.percentage_label.configure(text=f"{percentage:.0%}")
    
    def update_status(self, status):
        """Update the status label."""
        self.status_label.configure(text=status)
    
    def reset_progress(self):
        """Reset progress to initial state."""
        self.progress_bar.set(0)
        self.percentage_label.configure(text="0%")
        self.status_label.configure(text="Ready to download")