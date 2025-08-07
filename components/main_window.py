import os
import customtkinter as ctk
from tkinter import messagebox
from components.header_component import HeaderComponent
from components.url_input_component import URLInputComponent
from components.video_preview_component import VideoPreviewComponent
from components.download_settings_component import DownloadSettingsComponent
from components.progress_component import ProgressComponent
from components.footer_component import FooterComponent
from services.video_info_service import VideoInfoService
from services.download_service import DownloadService
from utils.validators import URLValidator

class MainWindow:
    """Main application window containing all components."""
    
    def __init__(self):
        self.window = ctk.CTk()
        self._setup_window()
        self._setup_services()
        self._setup_components()
    
    def _setup_window(self):
        """Setup the main window properties."""
        self.window.title("YouTube Downloader Pro")
        self.window.geometry("950x750")
        self.window.configure(fg_color="#1a1a1a")
        self.window.resizable(False, False)
    
    def _setup_services(self):
        """Initialize service classes."""
        self.video_info_service = VideoInfoService(self._on_video_info_received)
        self.download_service = DownloadService(
            progress_callback=self._on_progress_update,
            status_callback=self._on_status_update,
            completion_callback=self._on_download_complete
        )
    
    def _setup_components(self):
        """Setup all UI components."""
        # Main container
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Header
        self.header = HeaderComponent(self.main_frame)
        self.header.pack(fill="x", pady=(0, 20))
        
        # URL Input
        self.url_input = URLInputComponent(self.main_frame, self._on_url_change)
        self.url_input.pack(fill="x", pady=(0, 15))
        
        # Video Preview (initially hidden)
        self.video_preview = VideoPreviewComponent(self.main_frame)
        
        # Download Settings
        self.download_settings = DownloadSettingsComponent(self.main_frame)
        self.download_settings.pack(fill="x", pady=(0, 15))
        
        # Download Button
        self.download_button = ctk.CTkButton(
            self.main_frame,
            text="DOWNLOAD",
            width=200,
            height=45,
            command=self._start_download,
            font=("Arial", 14, "bold"),
            fg_color="#4d90fe",
            hover_color="#3a7bd5",
            corner_radius=8
        )
        self.download_button.pack(pady=20)
        
        # Progress
        self.progress = ProgressComponent(self.main_frame)
        self.progress.pack(fill="x", pady=(0, 15))
        
        # Footer
        self.footer = FooterComponent(self.main_frame)
        self.footer.pack(fill="x", side="bottom", pady=(10, 0), anchor="s")
    
    def _on_url_change(self, url):
        """Handle URL input changes."""
        if url and URLValidator.validate_url(url) and not URLValidator.is_playlist(url):
            # Only show preview for single videos, not playlists
            self.video_info_service.fetch_video_info(url)
        else:
            self._hide_preview()
    
    def _on_video_info_received(self, status, data):
        """Handle video information received from service."""
        if status == 'success' and data:
            thumbnail_image = None
            if data['thumbnail_url']:
                thumbnail_image = self.video_info_service.load_thumbnail(data['thumbnail_url'])
            
            self.video_preview.update_preview(
                data['title'],
                data['duration'],
                data['uploader'],
                data['view_count'],
                thumbnail_image
            )
            self._show_preview()
        else:
            self._hide_preview()
    
    def _show_preview(self):
        """Show the video preview component."""
        self.video_preview.pack(fill="x", pady=(0, 15), after=self.url_input)
    
    def _hide_preview(self):
        """Hide the video preview component."""
        self.video_preview.pack_forget()
    
    def _start_download(self):
        """Start the download process."""
        url = self.url_input.get_url()
        download_path = self.download_settings.get_download_path()
        download_type = self.download_settings.get_download_type()
        media_type = self.download_settings.get_media_type()
        quality_selection = self.download_settings.get_quality_selection()
        
        # Validation
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        
        if not download_path:
            messagebox.showerror("Error", "Please select a download location.")
            return
        
        if not URLValidator.validate_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL format. Please enter a valid video or playlist URL.")
            return
        
        is_url_playlist = URLValidator.is_playlist(url)
        
        if download_type == "playlist" and not is_url_playlist:
            messagebox.showerror("Error", "You selected 'Playlist' but the URL is not a playlist URL.")
            return
        
        if download_type == "video" and is_url_playlist:
            messagebox.showerror("Error", "You selected 'Single Video' but the URL is a playlist URL. Please select 'Playlist' instead.")
            return
        
        # Disable UI and start download
        self._set_ui_state("disabled")
        self.download_service.start_download(url, download_path, download_type, media_type, quality_selection)
    
    def _on_progress_update(self, percentage):
        """Handle progress updates from download service."""
        self.window.after(0, lambda: self.progress.update_progress(percentage))
    
    def _on_status_update(self, status):
        """Handle status updates from download service."""
        self.window.after(0, lambda: self.progress.update_status(status))
    
    def _on_download_complete(self, status, message):
        """Handle download completion."""
        self.window.after(0, lambda: self._reset_ui_after_download())
        
        if status == "success":
            self.window.after(0, lambda: messagebox.showinfo("Success", message))
        else:
            self.window.after(0, lambda: messagebox.showerror("Error", message))
    
    def _set_ui_state(self, state):
        """Set the state of UI controls."""
        self.download_button.configure(state=state)
        self.url_input.set_state(state)
        self.download_settings.set_controls_state(state)
    
    def _reset_ui_after_download(self):
        """Reset UI after download completion."""
        self._set_ui_state("normal")
        self.progress.reset_progress()
    
    def run(self):
        """Start the application main loop."""
        self.window.mainloop()