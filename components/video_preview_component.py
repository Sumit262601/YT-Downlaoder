import customtkinter as ctk

class VideoPreviewComponent(ctk.CTkFrame):
    """Video preview component showing thumbnail and metadata."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="#252525", corner_radius=10)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the video preview UI elements."""
        self.preview_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.preview_content_frame.pack(pady=15, padx=15, fill="x")
        
        # Thumbnail
        self.thumbnail_label = ctk.CTkLabel(
            self.preview_content_frame,
            text="",
            width=180,
            height=100,
            corner_radius=8,
            fg_color="#333333"
        )
        self.thumbnail_label.pack(side="left", padx=10)
        
        # Video info
        self.info_frame = ctk.CTkFrame(self.preview_content_frame, fg_color="transparent")
        self.info_frame.pack(side="left", padx=10, fill="both", expand=True)
        
        self.title_label_preview = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=("Arial", 16, "bold"),
            wraplength=500,
            anchor="w",
            text_color="#ffffff"
        )
        self.title_label_preview.pack(anchor="w", pady=(0, 5))
        
        # Metadata grid
        self._setup_metadata_grid()
    
    def _setup_metadata_grid(self):
        """Setup the metadata grid layout."""
        self.metadata_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.metadata_frame.pack(anchor="w", fill="x")
        
        # Duration
        self.duration_frame = ctk.CTkFrame(self.metadata_frame, fg_color="transparent")
        self.duration_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        ctk.CTkLabel(self.duration_frame, text="⏱️ Duration:", font=("Arial", 12), text_color="#aaaaaa").pack(side="left")
        self.duration_label = ctk.CTkLabel(self.duration_frame, text="", font=("Arial", 12, "bold"), text_color="#ffffff")
        self.duration_label.pack(side="left")
        
        # Uploader
        self.uploader_frame = ctk.CTkFrame(self.metadata_frame, fg_color="transparent")
        self.uploader_frame.grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(self.uploader_frame, text="👤 Channel:", font=("Arial", 12), text_color="#aaaaaa").pack(side="left")
        self.uploader_label = ctk.CTkLabel(self.uploader_frame, text="", font=("Arial", 12, "bold"), text_color="#ffffff")
        self.uploader_label.pack(side="left")
        
        # Views
        self.views_frame = ctk.CTkFrame(self.metadata_frame, fg_color="transparent")
        self.views_frame.grid(row=1, column=0, sticky="w", pady=(10, 0), padx=(0, 20))
        
        ctk.CTkLabel(self.views_frame, text="👁️ Views:", font=("Arial", 12), text_color="#aaaaaa").pack(side="left")
        self.view_count_label = ctk.CTkLabel(self.views_frame, text="", font=("Arial", 12, "bold"), text_color="#ffffff")
        self.view_count_label.pack(side="left")
    
    def update_preview(self, title, duration, uploader, view_count, thumbnail_image=None):
        """Update the preview with video information."""
        self.title_label_preview.configure(text=title)
        self.duration_label.configure(text=duration)
        self.uploader_label.configure(text=uploader)
        self.view_count_label.configure(text=view_count)
        
        if thumbnail_image:
            self.thumbnail_label.configure(image=thumbnail_image, text="")
            self.thumbnail_label.image = thumbnail_image  # Keep reference
        else:
            self.thumbnail_label.configure(image="", text="No Thumbnail")