import os
import customtkinter as ctk
from tkinter import messagebox
from components.header_component import HeaderComponent
from components.url_input_component import URLInputComponent
from components.video_preview_component import VideoPreviewComponent
from components.playlist_component import PlaylistSelectionComponent
from components.download_settings_component import DownloadSettingsComponent
from components.progress_component import ProgressComponent
from components.footer_component import FooterComponent
from services.video_info_service import VideoInfoService
from services.playlist_info_service import PlaylistInfoService
from services.download_service import DownloadService
from utils.validators import URLValidator

class MainWindow:
    """Main application window with playlist selection support."""
    
    def __init__(self):
        self.window = ctk.CTk()
        self.current_playlist_url = ""
        self.selected_video_data = []
        self._setup_window()
        self._setup_services()
        self._setup_components()
    
    def _setup_window(self):
        """Setup the main window properties."""
        self.window.title("YouTube Downloader Pro")
        self.window.geometry("950x800")  # Increased height for playlist
        self.window.configure(fg_color="#1a1a1a")
        self.window.resizable(True, True)  # Allow resizing for playlist view
    
    def _setup_services(self):
        """Initialize service classes."""
        self.video_info_service = VideoInfoService(self._on_video_info_received)
        self.playlist_info_service = PlaylistInfoService(self._on_playlist_info_received)
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
        
        # Playlist Selection (initially hidden)
        self.playlist_selection = PlaylistSelectionComponent(
            self.main_frame,
            self._on_playlist_download,
            self._on_playlist_cancel
        )
        
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
        print(f"URL Changed: {url}")
        
        if not url:
            print("Empty URL - hiding previews")
            self._hide_all_previews()
            return
        
        if not URLValidator.validate_url(url):
            print("Invalid URL - hiding previews")
            self._hide_all_previews()
            return
        
        if URLValidator.is_playlist(url):
            print("Playlist URL detected - fetching playlist info")
            self._hide_video_preview()
            self.playlist_info_service.fetch_playlist_info(url)
            self.current_playlist_url = url
        elif URLValidator.is_single_video(url):
            print("Single video URL detected - fetching video info")
            self._hide_playlist_selection()
            self.video_info_service.fetch_video_info(url)
            self.current_playlist_url = ""
        else:
            print("Unknown URL type - hiding previews")
            self._hide_all_previews()
    
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
            self._show_video_preview()
        else:
            self._hide_video_preview()
    
    def _on_playlist_info_received(self, status, error_msg, playlist_info, video_list):
        """Handle playlist information received from service."""
        if status == 'success' and playlist_info and video_list:
            self.playlist_selection.update_playlist_info(playlist_info)
            self.playlist_selection.populate_video_list(video_list)
            self._show_playlist_selection()
            
            # Hide download button and settings when playlist is shown
            self.download_button.pack_forget()
            self.download_settings.pack_forget()
        else:
            print(f"Playlist fetch error: {error_msg}")
            self._hide_playlist_selection()
            if error_msg:
                messagebox.showerror("Playlist Error", error_msg)
    
    def _on_playlist_download(self, selected_indices, selected_videos):
        """Handle playlist download request."""
        self.selected_video_data = selected_videos
        
        # Show download settings and button again
        self.download_settings.pack(fill="x", pady=(0, 15), before=self.progress)
        self.download_button.pack(pady=20, before=self.progress)
        
        # Update download button text
        video_count = len(selected_videos)
        self.download_button.configure(text=f"DOWNLOAD {video_count} VIDEOS")
        
        # Hide playlist selection
        self._hide_playlist_selection()
        
        # Auto-start download or show settings
        download_path = self.download_settings.get_download_path()
        if download_path:
            self._start_playlist_download(selected_videos)
    
    def _on_playlist_cancel(self):
        """Handle playlist cancel."""
        self._hide_playlist_selection()
        self.url_input.url_entry.delete(0, ctk.END)
        self.current_playlist_url = ""
        
        # Show download settings and button again
        self.download_settings.pack(fill="x", pady=(0, 15), before=self.progress)
        self.download_button.pack(pady=20, before=self.progress)
        self.download_button.configure(text="DOWNLOAD")
    
    def _show_video_preview(self):
        """Show the video preview component."""
        self.video_preview.pack(fill="x", pady=(0, 15), after=self.url_input)
    
    def _hide_video_preview(self):
        """Hide the video preview component."""
        self.video_preview.pack_forget()
    
    def _show_playlist_selection(self):
        """Show the playlist selection component."""
        self.playlist_selection.pack(fill="both", expand=True, pady=(0, 15), after=self.url_input)
    
    def _hide_playlist_selection(self):
        """Hide the playlist selection component."""
        self.playlist_selection.pack_forget()
    
    def _hide_all_previews(self):
        """Hide all preview components."""
        self._hide_video_preview()
        self._hide_playlist_selection()
    
    def _start_download(self):
        """Start the download process."""
        url = self.url_input.get_url()
        download_path = self.download_settings.get_download_path()
        
        # Check if this is a playlist download with selected videos
        if self.selected_video_data:
            self._start_playlist_download(self.selected_video_data)
            return
        
        # Regular single video download
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
            messagebox.showerror("Error", "Invalid YouTube URL format.")
            return
        
        # Disable UI and start download
        self._set_ui_state("disabled")
        self.download_service.start_download(url, download_path, download_type, media_type, quality_selection)
    
    def _start_playlist_download(self, selected_videos):
        """Start downloading selected playlist videos."""
        download_path = self.download_settings.get_download_path()
        media_type = self.download_settings.get_media_type()
        quality_selection = self.download_settings.get_quality_selection()
        
        if not download_path:
            messagebox.showerror("Error", "Please select a download location.")
            return
        
        # Disable UI and start download
        self._set_ui_state("disabled")
        
        # Use custom playlist download method
        self.download_service.start_playlist_download(
            selected_videos, download_path, media_type, quality_selection
        )
    
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
        self.selected_video_data = []
        self.download_button.configure(text="DOWNLOAD")
    
    def run(self):
        """Start the application main loop."""
        self.window.mainloop()