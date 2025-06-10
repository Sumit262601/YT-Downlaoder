import os
import sys
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox
import re
import threading
import yt_dlp
from pathlib import Path

class YouTubeDownloader:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("HD YouTube Downloader")
        self.window.geometry("800x580")
        self.window.configure(fg_color="#2b2b2b")

        self.total_videos = 0
        self.downloaded_videos = 0

        # Title
        self.title_label = ctk.CTkLabel(self.window, text="HD YouTube Downloader", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=20)

        # URL input
        self.url_frame = ctk.CTkFrame(self.window)
        self.url_frame.pack(pady=15, padx=20, fill="x")

        self.url_label = ctk.CTkLabel(self.url_frame, text="YouTube URL:", font=("Arial", 14))
        self.url_label.pack(side="left", padx=10)

        self.url_entry = ctk.CTkEntry(self.url_frame, width=600, height=35,
                                      placeholder_text="Paste YouTube URL or Playlist URL here...")
        self.url_entry.pack(side="left", padx=10)

        # Path selection
        self.path_frame = ctk.CTkFrame(self.window)
        self.path_frame.pack(pady=15, padx=20, fill="x")

        self.path_label = ctk.CTkLabel(self.path_frame, text="Download Path:", font=("Arial", 14))
        self.path_label.pack(side="left", padx=10)

        self.path_entry = ctk.CTkEntry(self.path_frame, width=480, height=35,
                                       placeholder_text="No download path selected")
        self.path_entry.pack(side="left", padx=10)
        self.path_entry.configure(state="readonly")

        self.browse_button = ctk.CTkButton(self.path_frame, text="Browse", command=self.browse_download_path, width=100)
        self.browse_button.pack(side="left", padx=10)

        # Options
        self.options_flex_frame = ctk.CTkFrame(self.window)
        self.options_flex_frame.pack(pady=15, padx=20, fill="x")

        # Quality Selection (Left)
        self.quality_label = ctk.CTkLabel(self.options_flex_frame, text="Select Quality:", font=("Arial", 14))
        self.quality_label.pack(side="left", padx=(10, 5))

        self.quality_var = ctk.StringVar(value="1080p")
        resolutions = ["2160p (4K)", "1440p (2K)", "1080p", "720p"]
        self.quality_menu = ctk.CTkOptionMenu(self.options_flex_frame, values=resolutions, 
                                            variable=self.quality_var, width=150)
        self.quality_menu.pack(side="left", padx=(0, 20))

        # Download Type Selection (Right)
        self.type_label = ctk.CTkLabel(self.options_flex_frame, text="Download Type:", font=("Arial", 14))
        self.type_label.pack(side="left", padx=(150, 5))

        self.download_type_var = ctk.StringVar(value="Single Video")
        self.single_video_radio = ctk.CTkRadioButton(self.options_flex_frame, text="Single Video",
                                                    variable=self.download_type_var, value="Single Video")
        self.single_video_radio.pack(side="left", padx=(0, 10))

        self.playlist_radio = ctk.CTkRadioButton(self.options_flex_frame, text="Playlist",
                                                variable=self.download_type_var, value="Playlist")
        self.playlist_radio.pack(side="left", padx=(0, 10))

        # Download Button
        self.download_button = ctk.CTkButton(self.window, text="Download Video/Playlist", width=200, height=40,
                                             command=self.download_content, font=("Arial", 14, "bold"))
        self.download_button.pack(pady=20)

        # Progress Bar
        self.progress_label = ctk.CTkLabel(self.window, text="Download Progress:", font=("Arial", 12))
        self.progress_label.pack(pady=(10, 5))

        self.progress_bar = ctk.CTkProgressBar(self.window, width=400)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        # Status Label
        self.status_label = ctk.CTkLabel(self.window, text="Ready to download", font=("Arial", 12))
        self.status_label.pack(pady=10)

        # Footer
        self.publisher_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.publisher_frame.pack(side="bottom", pady=10)

        self.publisher_label = ctk.CTkLabel(self.publisher_frame,
                                            text="© 2025 Your Company Name | Version 1.0",
                                            font=("Arial", 10), text_color="gray")
        self.publisher_label.pack()

    def validate_url(self, url, is_playlist=False):
        """
        Validate YouTube URL format
        
        Args:
            url (str): The URL to validate
            is_playlist (bool): Whether to validate as playlist URL
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Basic URL validation
        if not url.strip():
            return False
        
        # Check if it's a valid YouTube URL
        base_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/'
        
        if is_playlist:
            # Playlist URL pattern
            playlist_pattern = base_pattern + r'playlist\?list=.+'
            return re.match(playlist_pattern, url) is not None
        else:
            # Video URL pattern
            video_pattern = base_pattern + r'watch\?v=.+'
            return re.match(video_pattern, url) is not None

    def browse_download_path(self):
        """
        Open a file dialog to select the download path
        """
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder_selected)
            self.path_entry.configure(state="readonly")

    def download_content(self):
        """
        Download the video or playlist based on the provided URL and options
        """
        url = self.url_entry.get().strip()
        download_path = self.path_entry.get().strip()
        quality = self.quality_var.get()
        download_type = self.download_type_var.get()
        is_playlist = download_type == "Playlist"

        # Input validation
        if not url or not download_path:
            messagebox.showerror("Error", "Please provide both URL and download path")
            return

        if not self.validate_url(url, is_playlist):
            messagebox.showerror("Error", "Invalid YouTube URL format")
            return

        if not os.path.exists(download_path):
            messagebox.showerror("Error", "Selected download path does not exist")
            return

        # Disable UI elements during download
        self.download_button.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        self.quality_menu.configure(state="disabled")
        self.single_video_radio.configure(state="disabled")
        self.playlist_radio.configure(state="disabled")

        # Start download in a separate thread
        download_thread = threading.Thread(target=self.download_thread, args=(url, download_path, quality, is_playlist))
        download_thread.daemon = True
        download_thread.start()

    def download_thread(self, url, download_path, quality, is_playlist):
        """
        Handle the download process in a separate thread
        """
        try:
            self.status_label.configure(text="Initializing download...")
            self.progress_bar.set(0)
            
            # Configure yt-dlp options
            ydl_opts = self.get_download_options(download_path, quality, is_playlist)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video information
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise Exception("Could not fetch video information")

                # Set total videos count
                if is_playlist:
                    entries = info.get("entries", [])
                    self.total_videos = len([e for e in entries if e is not None])
                else:
                    self.total_videos = 1

                if self.total_videos == 0:
                    raise Exception("No valid videos found to download")

                # Start download
                self.status_label.configure(text=f"Starting download of {self.total_videos} video(s)...")
                ydl.download([url])

            # Download completed successfully
            self.status_label.configure(text="Download completed successfully!")
            messagebox.showinfo("Success", f"Downloaded {self.total_videos} video(s) successfully!")

        except Exception as e:
            self.status_label.configure(text="Error occurred during download!")
            messagebox.showerror("Error", f"Download failed: {str(e)}")

        finally:
            # Re-enable UI elements
            self.reset_ui()

    def get_download_options(self, download_path, quality, is_playlist):
        """
        Configure yt-dlp download options based on user selection
        """
        # Extract numerical quality value
        quality_value = quality.split()[0].replace('p', '')
        
        # Configure output template
        if is_playlist:
            outtmpl = os.path.join(download_path, '%(playlist_title)s', '%(playlist_index)s - %(title)s.%(ext)s')
        else:
            outtmpl = os.path.join(download_path, '%(title)s.%(ext)s')

        return {
            'format': f'bestvideo[height<={quality_value}]+bestaudio/best[height<={quality_value}]',
            'outtmpl': outtmpl,
            'progress_hooks': [self.progress_hook],
            'ignoreerrors': True,
            'noplaylist': not is_playlist,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': "in_playlist" if is_playlist else False,
            'merge_output_format': 'mp4',
        }

    def progress_hook(self, d):
        """
        Handle download progress updates
        """
        if d['status'] == 'downloading':
            # Calculate progress percentage
            if 'total_bytes' in d:
                percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d:
                percentage = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            else:
                percentage = 0
            
            # Update progress bar
            self.window.after(0, lambda: self.progress_bar.set(percentage / 100))
            
            # Update status with download speed and ETA
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)
            speed_str = f"{speed/1024/1024:.1f} MB/s" if speed else "N/A"
            eta_str = f"{eta//60}:{eta%60:02d}" if eta else "N/A"
            
            status_text = f"Downloading video {self.downloaded_videos + 1}/{self.total_videos} "
            status_text += f"({percentage:.1f}%) @ {speed_str} (ETA: {eta_str})"
            self.window.after(0, lambda: self.status_label.configure(text=status_text))

        elif d['status'] == 'finished':
            self.downloaded_videos += 1
            self.window.after(0, lambda: self.progress_bar.set(1))
            self.window.after(0, lambda: self.status_label.configure(
                text=f"Processing video {self.downloaded_videos}/{self.total_videos}..."
            ))

    def reset_ui(self):
        """
        Reset UI elements to their initial state
        """
        self.window.after(0, lambda: [
            self.download_button.configure(state="normal"),
            self.url_entry.configure(state="normal"),
            self.browse_button.configure(state="normal"),
            self.quality_menu.configure(state="normal"),
            self.single_video_radio.configure(state="normal"),
            self.playlist_radio.configure(state="normal"),
            self.progress_bar.set(0),
            setattr(self, 'downloaded_videos', 0),
            setattr(self, 'total_videos', 0)
        ])

    def run(self):
        """
        Start the application
        """
        self.window.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()
