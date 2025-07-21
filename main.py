import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import re
import threading
import yt_dlp
import certifi
import ssl
import time
import requests
from PIL import Image, ImageTk
from io import BytesIO

# Ensure certifi is being used for SSL certificates
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

class YouTubeDownloader:
    def __init__(self):
        # Main window setup
        self.window = ctk.CTk()
        self.window.title("YouTube Downloader Pro")
        self.window.geometry("950x750")
        self.window.configure(fg_color="#1a1a1a")
        self.window.resizable(False, False)

        # Variables to track playlist download progress
        self.current_video_index = 0
        self.total_playlist_videos = 0

        # Set custom theme colors
        ctk.set_default_color_theme("blue")
        
        # Create main container frame
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Header Section
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        # App logo and title
        self.logo_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.logo_frame.pack(side="left")
        
        # Placeholder for logo (you can replace with actual image)
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

        # URL Input Section
        self.url_frame = ctk.CTkFrame(self.main_frame, fg_color="#252525", corner_radius=10)
        self.url_frame.pack(fill="x", pady=(0, 15))
        
        self.url_label = ctk.CTkLabel(
            self.url_frame, 
            text="YouTube URL:",
            font=("Arial", 14),
            text_color="#cccccc"
        )
        self.url_label.pack(side="left", padx=(15, 10), pady=15)
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame, 
            width=600,
            height=40,
            placeholder_text="Paste video or playlist URL here...",
            fg_color="#333333",
            border_color="#4d90fe",
            text_color="#ffffff",
            placeholder_text_color="#999999"
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=15)
        self.url_entry.bind('<KeyRelease>', self.on_url_change)
        self.url_entry.bind('<FocusOut>', self.on_url_change)

        # Video Preview Section
        self.preview_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#252525", 
            corner_radius=10
        )
        self.preview_frame.pack(fill="x", pady=(0, 15))
        self.preview_frame.pack_forget()  # Initially hidden
        
        # Preview content
        self.preview_content_frame = ctk.CTkFrame(
            self.preview_frame, 
            fg_color="transparent"
        )
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
        self.info_frame = ctk.CTkFrame(
            self.preview_content_frame, 
            fg_color="transparent"
        )
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
        self.metadata_frame = ctk.CTkFrame(
            self.info_frame, 
            fg_color="transparent"
        )
        self.metadata_frame.pack(anchor="w", fill="x")
        
        # Row 1
        self.duration_frame = ctk.CTkFrame(
            self.metadata_frame, 
            fg_color="transparent"
        )
        self.duration_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        ctk.CTkLabel(
            self.duration_frame,
            text="⏱️ Duration:",
            font=("Arial", 12),
            text_color="#aaaaaa"
        ).pack(side="left")
        
        self.duration_label = ctk.CTkLabel(
            self.duration_frame,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#ffffff"
        )
        self.duration_label.pack(side="left")
        
        # Row 1, Column 2
        self.uploader_frame = ctk.CTkFrame(
            self.metadata_frame, 
            fg_color="transparent"
        )
        self.uploader_frame.grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(
            self.uploader_frame,
            text="👤 Channel:",
            font=("Arial", 12),
            text_color="#aaaaaa"
        ).pack(side="left")
        
        self.uploader_label = ctk.CTkLabel(
            self.uploader_frame,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#ffffff"
        )
        self.uploader_label.pack(side="left")
        
        # Row 2
        self.views_frame = ctk.CTkFrame(
            self.metadata_frame, 
            fg_color="transparent"
        )
        self.views_frame.grid(row=1, column=0, sticky="w", pady=(10, 0), padx=(0, 20))
        
        ctk.CTkLabel(
            self.views_frame,
            text="👁️ Views:",
            font=("Arial", 12),
            text_color="#aaaaaa"
        ).pack(side="left")
        
        self.view_count_label = ctk.CTkLabel(
            self.views_frame,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#ffffff"
        )
        self.view_count_label.pack(side="left")

        # Download Settings Section
        self.settings_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#252525", 
            corner_radius=10
        )
        self.settings_frame.pack(fill="x", pady=(0, 15))
        
        # Path selection
        self.path_frame = ctk.CTkFrame(
            self.settings_frame, 
            fg_color="transparent"
        )
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
            command=self.browse_download_path,
            font=("Arial", 12),
            fg_color="#4d90fe",
            hover_color="#3a7bd5"
        )
        self.browse_button.pack(side="left")

        # Download options grid
        self.options_grid = ctk.CTkFrame(
            self.settings_frame, 
            fg_color="transparent"
        )
        self.options_grid.pack(fill="x", padx=15, pady=(0, 15))
        
        # Column 1: Download Type
        self.type_frame = ctk.CTkFrame(
            self.options_grid, 
            fg_color="transparent"
        )
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
        
        # Column 2: Media Type
        self.media_frame = ctk.CTkFrame(
            self.options_grid, 
            fg_color="transparent"
        )
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
            command=self.on_media_type_change,
            fg_color="#333333",
            button_color="#4d90fe",
            button_hover_color="#3a7bd5",
            text_color="#ffffff"
        )
        self.media_menu.pack(anchor="w")
        
        # Column 3: Quality/Format
        self.quality_frame = ctk.CTkFrame(
            self.options_grid, 
            fg_color="transparent"
        )
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

        # Download Button
        self.download_button = ctk.CTkButton(
            self.main_frame,
            text="DOWNLOAD",
            width=200,
            height=45,
            command=self.start_download,
            font=("Arial", 14, "bold"),
            fg_color="#4d90fe",
            hover_color="#3a7bd5",
            corner_radius=8
        )
        self.download_button.pack(pady=20)

        # Progress Section
        self.progress_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#252525", 
            corner_radius=10
        )
        self.progress_frame.pack(fill="x", pady=(0, 15))
        
        self.progress_top_frame = ctk.CTkFrame(
            self.progress_frame, 
            fg_color="transparent"
        )
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
            self.progress_frame,
            width=400,
            height=8,
            progress_color="#4d90fe"
        )
        self.progress_bar.pack(pady=(0, 15))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready to download",
            font=("Arial", 12),
            text_color="#aaaaaa"
        )
        self.status_label.pack(pady=(0, 15))

        # Footer
        self.footer_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="transparent"
        )
        self.footer_frame.pack(fill="x", side="bottom", pady=(10, 0), anchor="s")
        
        self.publisher_label = ctk.CTkLabel(
            self.footer_frame,
            text="© 2025 YouTube Downloader Pro | v2.0",
            font=("Arial", 10),
            text_color="#666666"
        )
        self.publisher_label.pack()

    def on_url_change(self, event=None):
        """Handle URL input changes to fetch video preview."""
        url = self.url_entry.get().strip()
        if url and self.validate_url(url) and not self.is_playlist(url):
            # Only show preview for single videos, not playlists
            threading.Thread(target=self.fetch_video_info, args=(url,), daemon=True).start()
        else:
            # Hide preview if URL is empty, invalid, or is a playlist
            self.hide_preview()

    def fetch_video_info(self, url):
        """Fetch video information and thumbnail."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'nocheckcertificate': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info:
                    # Extract video details
                    title = info.get('title', 'Unknown Title')
                    duration = self.format_duration(info.get('duration', 0))
                    uploader = info.get('uploader', 'Unknown')
                    view_count = self.format_view_count(info.get('view_count', 0))
                    thumbnail_url = info.get('thumbnail')
                    
                    # Update UI in main thread
                    self.window.after(0, lambda: self.update_preview(title, duration, uploader, view_count, thumbnail_url))
                
        except Exception as e:
            print(f"Error fetching video info: {e}")
            self.window.after(0, self.hide_preview)

    def format_duration(self, seconds):
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

    def format_view_count(self, count):
        """Format view count to readable format."""
        if not count:
            return "Unknown views"
        
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M views"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K views"
        else:
            return f"{count} views"

    def load_thumbnail(self, url):
        """Load thumbnail image from URL."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                # Resize image to fit the label
                image = image.resize((180, 100), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
        return None

    def update_preview(self, title, duration, uploader, view_count, thumbnail_url):
        """Update the preview section with video information."""
        # Update text information
        self.title_label_preview.configure(text=title)
        self.duration_label.configure(text=duration)
        self.uploader_label.configure(text=uploader)
        self.view_count_label.configure(text=view_count)
        
        # Load and set thumbnail
        if thumbnail_url:
            thumbnail_image = self.load_thumbnail(thumbnail_url)
            if thumbnail_image:
                self.thumbnail_label.configure(image=thumbnail_image, text="")
                # Keep a reference to prevent garbage collection
                self.thumbnail_label.image = thumbnail_image
            else:
                self.thumbnail_label.configure(image="", text="No Thumbnail")
        else:
            self.thumbnail_label.configure(image="", text="No Thumbnail")
        
        # Show the preview frame
        self.preview_frame.pack(fill="x", pady=(0, 15), after=self.url_frame)

    def hide_preview(self):
        """Hide the video preview section."""
        self.preview_frame.pack_forget()

    def on_media_type_change(self, choice):
        """Update quality options based on media type selection."""
        if choice == "Audio Only":
            self.quality_label.configure(text="Select Format:")
            self.quality_menu.configure(values=self.audio_formats)
            self.quality_var.set("MP3 (128kbps)")
        else:  # Video
            self.quality_label.configure(text="Select Quality:")
            self.quality_menu.configure(values=self.video_resolutions)
            self.quality_var.set("1080p")

    def browse_download_path(self):
        """Opens a file dialog to select the download directory."""
        folder_selected = filedialog.askdirectory(title="Select Download Location")
        if folder_selected:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, folder_selected)

    def validate_url(self, url):
        """Validate YouTube URL format for both videos and playlists."""
        video_regex = r'^(https?://)?(www\.)?(m\.)?(youtube\.com/watch\?v=|youtu\.be/)[A-Za-z0-9_-]{11}.*$'
        playlist_regex = r'^(https?://)?(www\.)?(m\.)?(youtube\.com/playlist\?list=)[A-Za-z0-9_-]+.*$'
        
        return bool(re.match(video_regex, url) or re.match(playlist_regex, url))

    def is_playlist(self, url):
        """Checks if the URL is a playlist URL."""
        return "playlist?list=" in url or "/playlist/" in url

    def get_format_options(self, media_type, quality_selection):
        """Get yt-dlp format options based on media type and quality."""
        if media_type == "Audio Only":
            # Audio format options
            if "MP3 (128kbps)" in quality_selection:
                return {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '128',
                    }],
                    'outtmpl_ext': 'mp3'
                }
            elif "MP3 (320kbps)" in quality_selection:
                return {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                    'outtmpl_ext': 'mp3'
                }
            elif "WAV" in quality_selection:
                return {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                    }],
                    'outtmpl_ext': 'wav'
                }
            elif "M4A" in quality_selection:
                return {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'm4a',
                    }],
                    'outtmpl_ext': 'm4a'
                }
        else:  # Video
            selected_quality = quality_selection.split()[0][:-1]  # Gets "2160" from "2160p (4K)"
            return {
                'format': f'bestvideo[height<={selected_quality}]+bestaudio/best',
                'format_sort': [
                    'res:2160',
                    'res:1440', 
                    'res:1080',
                    'res:720',
                    'fps'
                ],
                'merge_output_format': 'mp4',
                'outtmpl_ext': 'mp4'
            }

    def start_download(self):
        """Determines download type and starts the download in a separate thread."""
        url = self.url_entry.get().strip()
        download_path = self.path_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        
        if not download_path:
            messagebox.showerror("Error", "Please select a download location.")
            return

        if not self.validate_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL format. Please enter a valid video or playlist URL.")
            return

        is_url_playlist = self.is_playlist(url)
        selected_type = self.download_type_var.get()

        if selected_type == "playlist" and not is_url_playlist:
            messagebox.showerror("Error", "You selected 'Playlist' but the URL is not a playlist URL.")
            return
        
        if selected_type == "video" and is_url_playlist:
            messagebox.showerror("Error", "You selected 'Single Video' but the URL is a playlist URL. Please select 'Playlist' instead.")
            return

        thread = threading.Thread(target=self.download_content, args=(url, download_path, selected_type))
        thread.daemon = True
        thread.start()

    def download_content(self, url, download_path, selected_type):
        """Handles the actual download process for video or playlist."""
        try:
            self.window.after(0, lambda: self.status_label.configure(text="Fetching information..."))
            self.window.after(0, lambda: self.download_button.configure(state="disabled"))
            self.window.after(0, lambda: self.browse_button.configure(state="disabled"))
            self.window.after(0, lambda: self.url_entry.configure(state="disabled"))
            self.window.after(0, lambda: self.quality_menu.configure(state="disabled"))
            self.window.after(0, lambda: self.media_menu.configure(state="disabled"))
            self.window.after(0, lambda: self.video_radio.configure(state="disabled"))
            self.window.after(0, lambda: self.playlist_radio.configure(state="disabled"))
            self.window.after(0, lambda: self.path_entry.configure(state="disabled"))

            media_type = self.media_type_var.get()
            quality_selection = self.quality_var.get()
            format_options = self.get_format_options(media_type, quality_selection)

            ydl_opts = {
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True, 
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                'socket_timeout': 30,
                'retries': 5,
                'fragment_retries': 5,
                'extractor_retries': 5,
            }

            # Add format-specific options
            ydl_opts.update(format_options)

            # Set output template based on media type and download type
            file_ext = format_options.get('outtmpl_ext', 'mp4')
            if selected_type == "playlist":
                # First, extract info to get the total number of entries in the playlist
                self.window.after(0, lambda: self.status_label.configure(text="Fetching playlist info..."))
                try:
                    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True, 'force_generic_extractor': True, 'nocheckcertificate': True}) as ydl_info:
                        info_dict = ydl_info.extract_info(url, download=False)
                        if info_dict and info_dict.get('_type') == 'playlist':
                            self.total_playlist_videos = len(info_dict.get('entries', []))
                        else:
                            self.total_playlist_videos = 1
                except Exception as e:
                    print(f"Error fetching playlist info: {str(e)}")
                    self.total_playlist_videos = 1

                ydl_opts['outtmpl'] = os.path.join(download_path, '%(playlist)s', f'%(title)s.{file_ext}')
                ydl_opts['extract_flat'] = False
            else:  # Single video
                ydl_opts['outtmpl'] = os.path.join(download_path, f'%(title)s.{file_ext}')
                self.total_playlist_videos = 1
                self.current_video_index = 0

            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        self.window.after(0, lambda: self.status_label.configure(text="Downloading..."))
                        info = ydl.extract_info(url, download=True)
                        break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(f"Download failed after {max_retries} attempts: {str(e)}")
                    time.sleep(2)

            self.window.after(0, lambda: self.status_label.configure(text="Download Complete!"))
            self.window.after(0, lambda: messagebox.showinfo("Success", f"Content downloaded successfully to:\n{download_path}"))

        except Exception as e:
            error_msg = str(e)
            self.window.after(0, lambda: self.status_label.configure(text="Error occurred!"))
            self.window.after(0, lambda: messagebox.showerror("Error", f"Download failed: {error_msg}"))
        
        finally:
            self.window.after(0, self.reset_ui)

    def reset_ui(self):
        """Reset UI elements after download or error."""
        self.window.after(0, lambda: self.download_button.configure(state="normal"))
        self.window.after(0, lambda: self.browse_button.configure(state="normal"))
        self.window.after(0, lambda: self.url_entry.configure(state="normal"))
        self.window.after(0, lambda: self.quality_menu.configure(state="normal"))
        self.window.after(0, lambda: self.media_menu.configure(state="normal"))
        self.window.after(0, lambda: self.video_radio.configure(state="normal"))
        self.window.after(0, lambda: self.playlist_radio.configure(state="normal"))
        self.window.after(0, lambda: self.path_entry.configure(state="normal"))
        self.window.after(0, lambda: self.progress_bar.set(0))
        self.window.after(0, lambda: self.percentage_label.configure(text="0%"))
        self.window.after(0, lambda: self.status_label.configure(text="Ready"))
        self.current_video_index = 0
        self.total_playlist_videos = 0

    def progress_hook(self, d):
        """Handle download progress updates."""
        if d['status'] == 'downloading':
            try:
                total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                percentage = 0
                if total_bytes:
                    percentage = downloaded / total_bytes
                
                self.window.after(0, lambda: self.progress_bar.set(percentage))
                self.window.after(0, lambda: self.percentage_label.configure(text=f"{percentage:.0%}"))
                
                current_status_text = ""
                if self.total_playlist_videos > 1:
                    if d.get('info_dict', {}).get('playlist_index') is not None:
                        self.current_video_index = d['info_dict']['playlist_index']
                    
                    display_current_index = max(1, self.current_video_index)

                    current_status_text = (
                        f"Downloading item {display_current_index} of {self.total_playlist_videos}: "
                    )
                
                if total_bytes:
                    current_status_text += f"Downloaded: {percentage:.1%} of {d.get('_total_bytes_str', 'N/A')}"
                else:
                    current_status_text += f"Downloaded: {d.get('_downloaded_bytes_str', 'N/A')}"
                
                self.window.after(0, lambda: self.status_label.configure(text=current_status_text))
            except Exception:
                self.window.after(0, lambda: self.status_label.configure(text="Downloading... (progress update error)"))

        elif d['status'] == 'finished':
            self.window.after(0, lambda: self.progress_bar.set(1))
            self.window.after(0, lambda: self.percentage_label.configure(text="100%"))
            media_type = self.media_type_var.get()
            if media_type == "Audio Only":
                self.window.after(0, lambda: self.status_label.configure(text="Converting to audio format..."))
            else:
                self.window.after(0, lambda: self.status_label.configure(text="Processing and merging files..."))

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()