import os
import customtkinter as ctk
from tkinter import filedialog

class DownloadSettingsComponent(ctk.CTkFrame):
    """Download settings component with path selection and options."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="#252525", corner_radius=10)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the download settings UI elements."""
        self._setup_path_selection()
        self._setup_download_options()
    
    def _setup_path_selection(self):
        """Setup path selection controls."""
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(fill="x", padx=15, pady=15)
        
        self.path_label = ctk.CTkLabel(
            self.path_frame,
            text="Download Location:",
            font=("Arial", 14),
            text_color="#cccccc"
        )
        self.path_label.pack(side="left", padx=(0, 10))
        
        self.path_entry = ctk.CTkEntry(
            self.path_frame,
            width=400,
            height=35,
            placeholder_text="Select download folder...",
            fg_color="#333333",
            border_color="#4d90fe",
            text_color="#ffffff"
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.path_entry.insert(0, os.path.join(os.path.expanduser("~"), "Downloads"))
        
        self.browse_button = ctk.CTkButton(
            self.path_frame,
            text="Browse",
            width=100,
            height=35,
            command=self._browse_download_path,
            font=("Arial", 12),
            fg_color="#4d90fe",
            hover_color="#3a7bd5"
        )
        self.browse_button.pack(side="left")
    
    def _setup_download_options(self):
        """Setup download options grid."""
        self.options_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.options_grid.pack(fill="x", padx=15, pady=(0, 15))
        
        # Download Type
        self._setup_download_type()
        
        # Media Type
        self._setup_media_type()
        
        # Quality/Format
        self._setup_quality_options()
    
    def _setup_download_type(self):
        """Setup download type selection."""
        self.type_frame = ctk.CTkFrame(self.options_grid, fg_color="transparent")
        self.type_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            self.type_frame,
            text="Download Type:",
            font=("Arial", 14),
            text_color="#cccccc"
        ).pack(anchor="w", pady=(0, 5))
        
        self.download_type_var = ctk.StringVar(value="video")
        
        self.video_radio = ctk.CTkRadioButton(
            self.type_frame, 
            text="Single Video", 
            variable=self.download_type_var, 
            value="video",
            font=("Arial", 12),
            text_color="#ffffff",
            hover_color="#4d90fe"
        )
        self.video_radio.pack(anchor="w", pady=2)
        
        self.playlist_radio = ctk.CTkRadioButton(
            self.type_frame, 
            text="Playlist", 
            variable=self.download_type_var, 
            value="playlist",
            font=("Arial", 12),
            text_color="#ffffff",
            hover_color="#4d90fe"
        )
        self.playlist_radio.pack(anchor="w", pady=2)
    
    def _setup_media_type(self):
        """Setup media type selection."""
        self.media_frame = ctk.CTkFrame(self.options_grid, fg_color="transparent")
        self.media_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            self.media_frame,
            text="Media Type:",
            font=("Arial", 14),
            text_color="#cccccc"
        ).pack(anchor="w", pady=(0, 5))
        
        self.media_type_var = ctk.StringVar(value="Video")
        self.media_menu = ctk.CTkOptionMenu(
            self.media_frame,
            values=["Video", "Audio Only"],
            variable=self.media_type_var,
            width=150,
            height=30,
            font=("Arial", 12),
            dropdown_font=("Arial", 12),
            command=self._on_media_type_change,
            fg_color="#333333",
            button_color="#4d90fe",
            button_hover_color="#3a7bd5",
            text_color="#ffffff"
        )
        self.media_menu.pack(anchor="w")
    
    def _setup_quality_options(self):
        """Setup quality/format selection."""
        self.quality_frame = ctk.CTkFrame(self.options_grid, fg_color="transparent")
        self.quality_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
        
        self.quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="Select Quality:",
            font=("Arial", 14),
            text_color="#cccccc"
        )
        self.quality_label.pack(anchor="w", pady=(0, 5))
        
        self.quality_var = ctk.StringVar(value="1080p")
        self.video_resolutions = ["2160p (4K)", "1440p (2K)", "1080p", "720p"]
        self.audio_formats = ["MP3 (128kbps)", "MP3 (320kbps)", "WAV", "M4A"]
        
        self.quality_menu = ctk.CTkOptionMenu(
            self.quality_frame,
            values=self.video_resolutions,
            variable=self.quality_var,
            width=150,
            height=30,
            font=("Arial", 12),
            dropdown_font=("Arial", 12),
            fg_color="#333333",
            button_color="#4d90fe",
            button_hover_color="#3a7bd5",
            text_color="#ffffff"
        )
        self.quality_menu.pack(anchor="w")
    
    def _browse_download_path(self):
        """Open file dialog to select download directory."""
        folder_selected = filedialog.askdirectory(title="Select Download Location")
        if folder_selected:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, folder_selected)
    
    def _on_media_type_change(self, choice):
        """Update quality options based on media type selection."""
        if choice == "Audio Only":
            self.quality_label.configure(text="Select Format:")
            self.quality_menu.configure(values=self.audio_formats)
            self.quality_var.set("MP3 (128kbps)")
        else:  # Video
            self.quality_label.configure(text="Select Quality:")
            self.quality_menu.configure(values=self.video_resolutions)
            self.quality_var.set("1080p")
    
    def get_download_path(self):
        """Get the selected download path."""
        return self.path_entry.get().strip()
    
    def get_download_type(self):
        """Get the selected download type."""
        return self.download_type_var.get()
    
    def get_media_type(self):
        """Get the selected media type."""
        return self.media_type_var.get()
    
    def get_quality_selection(self):
        """Get the selected quality/format."""
        return self.quality_var.get()
    
    def set_controls_state(self, state):
        """Set the state of all controls."""
        self.browse_button.configure(state=state)
        self.quality_menu.configure(state=state)
        self.media_menu.configure(state=state)
        self.video_radio.configure(state=state)
        self.playlist_radio.configure(state=state)
        self.path_entry.configure(state=state)