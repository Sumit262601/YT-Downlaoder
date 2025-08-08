import customtkinter as ctk
import threading
from tkinter import messagebox
from PIL import Image
import requests
from io import BytesIO


class PlaylistSelectionComponent(ctk.CTkFrame):
    """Playlist selection component with video list and checkboxes."""
    
    def __init__(self, parent, on_download_callback, on_cancel_callback):
        super().__init__(parent, fg_color="#252525", corner_radius=10)
        self.on_download_callback = on_download_callback
        self.on_cancel_callback = on_cancel_callback
        self.video_vars = {}  # Store checkbox variables
        self.video_data = []  # Store video information
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the playlist selection UI."""
        # Header with playlist info
        self.header_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=8)
        self.header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        # Playlist title
        self.playlist_title = ctk.CTkLabel(
            self.header_frame,
            text="Playlist Title",
            font=("Arial", 18, "bold"),
            text_color="#ffffff",
            wraplength=800
        )
        self.playlist_title.pack(pady=10)
        
        # Playlist metadata
        self.metadata_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.metadata_frame.pack(pady=(0, 10))
        
        # Channel name
        self.channel_frame = ctk.CTkFrame(self.metadata_frame, fg_color="transparent")
        self.channel_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(
            self.channel_frame,
            text="👤 Channel:",
            font=("Arial", 12),
            text_color="#aaaaaa"
        ).pack(side="left")
        
        self.channel_label = ctk.CTkLabel(
            self.channel_frame,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#ffffff"
        )
        self.channel_label.pack(side="left", padx=(5, 0))
        
        # Video count
        self.count_frame = ctk.CTkFrame(self.metadata_frame, fg_color="transparent")
        self.count_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(
            self.count_frame,
            text="📹 Videos:",
            font=("Arial", 12),
            text_color="#aaaaaa"
        ).pack(side="left")
        
        self.count_label = ctk.CTkLabel(
            self.count_frame,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#ffffff"
        )
        self.count_label.pack(side="left", padx=(5, 0))
        
        # Selection controls
        self.controls_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=8)
        self.controls_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Select all/none buttons
        self.select_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.select_frame.pack(pady=10)
        
        ctk.CTkLabel(
            self.select_frame,
            text="Select Videos:",
            font=("Arial", 14, "bold"),
            text_color="#cccccc"
        ).pack(side="left", padx=(0, 15))
        
        self.select_all_btn = ctk.CTkButton(
            self.select_frame,
            text="Select All",
            width=100,
            height=30,
            command=self.select_all_videos,
            font=("Arial", 11),
            fg_color="#4d90fe",
            hover_color="#3a7bd5"
        )
        self.select_all_btn.pack(side="left", padx=5)
        
        self.select_none_btn = ctk.CTkButton(
            self.select_frame,
            text="Select None",
            width=100,
            height=30,
            command=self.select_no_videos,
            font=("Arial", 11),
            fg_color="#666666",
            hover_color="#555555"
        )
        self.select_none_btn.pack(side="left", padx=5)
        
        # Selected count
        self.selected_label = ctk.CTkLabel(
            self.select_frame,
            text="Selected: 0 videos",
            font=("Arial", 12),
            text_color="#4d90fe"
        )
        self.selected_label.pack(side="left", padx=(15, 0))
        
        # Scrollable video list
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=880,
            height=300,
            fg_color="#1a1a1a",
            # scrollbar_color="#333333",
            scrollbar_button_color="#555555"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Action buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.cancel_btn = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            width=120,
            height=40,
            command=self.cancel_selection,
            font=("Arial", 12, "bold"),
            fg_color="#ff4444",
            hover_color="#cc3333"
        )
        self.cancel_btn.pack(side="left")
        
        self.download_selected_btn = ctk.CTkButton(
            self.button_frame,
            text="Download Selected",
            width=200,
            height=40,
            command=self.download_selected,
            font=("Arial", 12, "bold"),
            fg_color="#4d90fe",
            hover_color="#3a7bd5"
        )
        self.download_selected_btn.pack(side="right")
    
    def update_playlist_info(self, playlist_info):
        """Update playlist information display."""
        self.playlist_title.configure(text=playlist_info.get('title', 'Unknown Playlist'))
        self.channel_label.configure(text=playlist_info.get('uploader', 'Unknown Channel'))
        self.count_label.configure(text=str(len(playlist_info.get('entries', []))))
    
    def populate_video_list(self, video_list):
        """Populate the scrollable video list with checkboxes and thumbnails."""
        # Clear existing widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        self.video_vars.clear()
        self.video_data = video_list
    
        for i, video in enumerate(video_list):
            # Create video frame
            video_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#252525", corner_radius=8)
            video_frame.pack(fill="x", pady=5, padx=10)
            
            # Checkbox and video info frame
            content_frame = ctk.CTkFrame(video_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=10, pady=10)
            
            # Checkbox
            var = ctk.BooleanVar(value=True)  # Default selected
            self.video_vars[i] = var
            
            checkbox = ctk.CTkCheckBox(
                content_frame,
                text="",
                variable=var,
                width=20,
                height=20,
                command=self.update_selected_count,
                checkbox_width=20,
                checkbox_height=20,
                corner_radius=4
            )
            checkbox.pack(side="left", padx=(0, 10))
            
            # Thumbnail loading
            thumbnail_url = video.get('thumbnail')
            thumbnail_image = None
    
            if thumbnail_url:
                try:
                    response = requests.get(thumbnail_url, timeout=5)
                    image_data = Image.open(BytesIO(response.content)).convert("RGB")
                    image_data = image_data.resize((120, 68))
                    thumbnail_image = ctk.CTkImage(light_image=image_data, size=(120, 68))
                except Exception as e:
                    print(f"[Thumbnail Error] {e}")
            
            if thumbnail_image:
                thumbnail_label = ctk.CTkLabel(content_frame, image=thumbnail_image, text="")
                thumbnail_label.image = thumbnail_image  # Prevent garbage collection
                thumbnail_label.pack(side="left", padx=(0, 10))
            else:
                ctk.CTkLabel(content_frame, text="", width=120).pack(side="left", padx=(0, 10))
            
            # Video info
            info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)
            
            # Video number and title
            title_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            title_frame.pack(fill="x", anchor="w")
            
            video_number = ctk.CTkLabel(
                title_frame,
                text=f"#{i+1:02d}",
                font=("Arial", 12, "bold"),
                text_color="#4d90fe",
                width=40
            )
            video_number.pack(side="left")
            
            title_text = video.get('title', f'Video {i+1}')
            if len(title_text) > 80:
                title_text = title_text[:80] + "..."
            
            video_title = ctk.CTkLabel(
                title_frame,
                text=title_text,
                font=("Arial", 13, "bold"),
                text_color="#ffffff",
                anchor="w"
            )
            video_title.pack(side="left", fill="x", expand=True, padx=(10, 0))
            
            # Video metadata
            meta_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            meta_frame.pack(fill="x", anchor="w", pady=(5, 0))
            
            # Duration
            duration_text = self._format_duration(video.get('duration', 0))
            duration_label = ctk.CTkLabel(
                meta_frame,
                text=f"⏱️ {duration_text}",
                font=("Arial", 10),
                text_color="#aaaaaa"
            )
            duration_label.pack(side="left", padx=(50, 20))
            
            # View count
            view_count = self._format_view_count(video.get('view_count', 0))
            views_label = ctk.CTkLabel(
                meta_frame,
                text=f"👁️ {view_count}",
                font=("Arial", 10),
                text_color="#aaaaaa"
            )
            views_label.pack(side="left", padx=(0, 20))
            
            # Upload date (if available)
            if video.get('upload_date'):
                upload_date = video.get('upload_date', '')
                if len(upload_date) == 8:  # Format: YYYYMMDD
                    formatted_date = f"{upload_date[6:8]}/{upload_date[4:6]}/{upload_date[:4]}"
                    date_label = ctk.CTkLabel(
                        meta_frame,
                        text=f"📅 {formatted_date}",
                        font=("Arial", 10),
                        text_color="#aaaaaa"
                    )
                    date_label.pack(side="left")
    
        self.update_selected_count()

    
    def _format_duration(self, seconds):
        """Format duration from seconds to readable format."""
        if not seconds:
            return "Unknown"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def _format_view_count(self, count):
        """Format view count to readable format."""
        if not count:
            return "0 views"
        
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M views"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K views"
        else:
            return f"{count} views"
    
    def select_all_videos(self):
        """Select all videos."""
        for var in self.video_vars.values():
            var.set(True)
        self.update_selected_count()
    
    def select_no_videos(self):
        """Deselect all videos."""
        for var in self.video_vars.values():
            var.set(False)
        self.update_selected_count()
    
    def update_selected_count(self):
        """Update the selected count display."""
        selected_count = sum(1 for var in self.video_vars.values() if var.get())
        total_count = len(self.video_vars)
        
        self.selected_label.configure(text=f"Selected: {selected_count} of {total_count} videos")
        
        # Enable/disable download button based on selection
        if selected_count > 0:
            self.download_selected_btn.configure(state="normal")
        else:
            self.download_selected_btn.configure(state="disabled")
    
    def get_selected_videos(self):
        """Get list of selected video indices and data."""
        selected_indices = []
        selected_videos = []
        
        for i, var in self.video_vars.items():
            if var.get():
                selected_indices.append(i)
                if i < len(self.video_data):
                    selected_videos.append(self.video_data[i])
        
        return selected_indices, selected_videos
    
    def download_selected(self):
        """Handle download selected videos."""
        selected_indices, selected_videos = self.get_selected_videos()
        
        if not selected_videos:
            messagebox.showwarning("No Selection", "Please select at least one video to download.")
            return
        
        if self.on_download_callback:
            self.on_download_callback(selected_indices, selected_videos)
    
    def cancel_selection(self):
        """Handle cancel button."""
        if self.on_cancel_callback:
            self.on_cancel_callback()