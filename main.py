import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import re
import threading
import yt_dlp
import certifi
import ssl
import time

# Ensure certifi is being used for SSL certificates
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

class YouTubeDownloader:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("HD YouTube Downloader")
        self.window.geometry("800x650") # Slightly increased height for better spacing
        self.window.configure(fg_color="#2b2b2b")
        self.window.resizable(False, False)

        # Variables to track playlist download progress
        self.current_video_index = 0
        self.total_playlist_videos = 0

        # Title Label
        self.title_label = ctk.CTkLabel(
            self.window, 
            text="HD YouTube Downloader",
            font=("Arial", 34, "bold")
        )
        self.title_label.pack(pady=20)

        # URL Entry
        self.url_frame = ctk.CTkFrame(self.window)
        self.url_frame.pack(pady=10, padx=20, fill="x") # Reduced pady for tighter grouping
        
        self.url_label = ctk.CTkLabel(
            self.url_frame, 
            text="YouTube URL:",
            font=("Arial", 14)
        )
        self.url_label.pack(side="left", padx=10)
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame, 
            width=600,
            height=35,
            placeholder_text="Paste YouTube video or playlist URL here..."
        )
        self.url_entry.pack(side="left", padx=10)

        # Download Path Selection (Browse)
        self.path_frame = ctk.CTkFrame(self.window)
        self.path_frame.pack(pady=10, padx=20, fill="x") # Reduced pady for tighter grouping

        self.path_label = ctk.CTkLabel(
            self.path_frame,
            text="Download Path:",
            font=("Arial", 14)
        )
        self.path_label.pack(side="left", padx=10)

        self.path_entry = ctk.CTkEntry(
            self.path_frame,
            width=480,
            height=35,
            placeholder_text="Select download location..."
        )
        self.path_entry.pack(side="left", padx=10)
        self.path_entry.insert(0, os.path.join(os.path.expanduser("~"), "Downloads")) # Set default path

        self.browse_button = ctk.CTkButton(
            self.path_frame,
            text="Browse",
            width=100,
            height=35,
            command=self.browse_download_path,
            font=("Arial", 14)
        )
        self.browse_button.pack(side="left", padx=10)

        # Container frame for Download Type and Quality Options
        self.options_container_frame = ctk.CTkFrame(self.window)
        self.options_container_frame.pack(pady=15, padx=20, fill="x")
        
        # Download Type Selection - Separated
        self.type_frame = ctk.CTkFrame(self.options_container_frame)
        self.type_frame.pack(side="left", padx=20, pady=10, expand=True) # Added expand=True

        self.type_label = ctk.CTkLabel(
            self.type_frame,
            text="Download Type:",
            font=("Arial", 14)
        )
        self.type_label.pack(pady=(0, 5))

        self.download_type_var = ctk.StringVar(value="video") # Default to video
        self.video_radio = ctk.CTkRadioButton(
            self.type_frame, 
            text="Single Video", 
            variable=self.download_type_var, 
            value="video",
            font=("Arial", 14)
        )
        self.video_radio.pack(pady=5)

        self.playlist_radio = ctk.CTkRadioButton(
            self.type_frame, 
            text="Playlist", 
            variable=self.download_type_var, 
            value="playlist",
            font=("Arial", 14)
        )
        self.playlist_radio.pack(pady=5)

        # Resolution Options - Separated
        self.quality_frame = ctk.CTkFrame(self.options_container_frame)
        self.quality_frame.pack(side="right", padx=20, pady=10, expand=True) # Added expand=True
        
        self.quality_var = ctk.StringVar(value="1080p")
        resolutions = ["2160p (4K)", "1440p (2K)", "1080p", "720p"]
        
        self.quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="Select Quality:",
            font=("Arial", 14)
        )
        self.quality_label.pack(pady=(0, 5)) # Adjusted pady

        self.quality_menu = ctk.CTkOptionMenu(
            self.quality_frame,
            values=resolutions,
            variable=self.quality_var,
            width=150
        )
        self.quality_menu.pack(pady=5)

        # Download Button
        self.download_button = ctk.CTkButton(
            self.window,
            text="Download",
            width=200,
            height=40,
            command=self.start_download,
            font=("Arial", 14, "bold")
        )
        self.download_button.pack(pady=20)

        # Progress Bar
        self.progress_label = ctk.CTkLabel(
            self.window,
            text="Download Progress:",
            font=("Arial", 12)
        )
        self.progress_label.pack(pady=(20,5))
        
        self.progress_bar = ctk.CTkProgressBar(
            self.window,
            width=400
        )
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        # Status Label
        self.status_label = ctk.CTkLabel(
            self.window,
            text="Ready to download",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)

        # Add Publisher Info at the bottom
        self.publisher_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.publisher_frame.pack(side="bottom", pady=10)
        
        self.publisher_label = ctk.CTkLabel(
            self.publisher_frame,
            text="© 2025 YT-Downloader | Version 1.3", # Updated version
            font=("Arial", 10),
            text_color="gray"
        )
        self.publisher_label.pack()

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
            self.window.after(0, lambda: self.video_radio.configure(state="disabled"))
            self.window.after(0, lambda: self.playlist_radio.configure(state="disabled"))
            self.window.after(0, lambda: self.path_entry.configure(state="disabled"))

            selected_quality = self.quality_var.get().split()[0][:-1] # Gets "2160" from "2160p (4K)"

            ydl_opts = {
                'format': f'bestvideo[height<={selected_quality}]+bestaudio/best',
                'format_sort': [
                    'res:2160',
                    'res:1440',
                    'res:1080',
                    'res:720',
                    'fps'
                ],
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
                'merge_output_format': 'mp4',
            }

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
                    self.total_playlist_videos = 1  # Fallback in case of error

                ydl_opts['outtmpl'] = os.path.join(download_path, '%(playlist)s', '%(title)s.%(ext)s')
                ydl_opts['extract_flat'] = False # Ensure full extraction for playlist details and proper folder naming
            else: # Single video
                ydl_opts['outtmpl'] = os.path.join(download_path, '%(title)s.%(ext)s')
                self.total_playlist_videos = 1 # For single video, total is 1
                self.current_video_index = 0 # Reset for single video

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
                    time.sleep(2) # Wait before retrying

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
        self.window.after(0, lambda: self.video_radio.configure(state="normal"))
        self.window.after(0, lambda: self.playlist_radio.configure(state="normal"))
        self.window.after(0, lambda: self.path_entry.configure(state="normal"))
        self.window.after(0, lambda: self.progress_bar.set(0))
        self.window.after(0, lambda: self.status_label.configure(text="Ready"))
        self.current_video_index = 0 # Reset for next download
        self.total_playlist_videos = 0 # Reset for next download


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
                
                current_status_text = ""
                if self.total_playlist_videos > 1:
                    # For playlists, check if a new video has started downloading
                    # yt-dlp's playlist_index is 1-based. It might not be available in the very first hook for a video.
                    if d.get('info_dict', {}).get('playlist_index') is not None:
                        self.current_video_index = d['info_dict']['playlist_index']
                    
                    # Ensure current_video_index is at least 1 for display purposes
                    display_current_index = max(1, self.current_video_index)

                    current_status_text = (
                        f"Downloading video {display_current_index} of {self.total_playlist_videos}: "
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
            self.window.after(0, lambda: self.status_label.configure(text="Processing and merging files..."))

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()