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
        try:
            if not url:
                return False
            
            if is_playlist:
                pattern = r'^(https?://)?(www\.)?(youtube\.com/playlist\?list=[\w-]+)'
            else:
                pattern = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}(?:\S+)?$'
            
            return bool(re.match(pattern, url))
        except:
            return False

    def browse_download_path(self):
        download_directory = filedialog.askdirectory(title="Select Download Location")
        if download_directory:
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, download_directory)
            self.path_entry.configure(state="readonly")
            self.status_label.configure(text=f"Download path set to: {download_directory}")

    def download_content(self):
        thread = threading.Thread(target=self.download_content_thread)
        thread.daemon = True
        thread.start()

    def download_content_thread(self):
        try:
            # Input validation
            url = self.url_entry.get().strip()
            is_playlist = self.download_type_var.get() == "Playlist"
            download_path = self.path_entry.get().strip()

            # Validate inputs
            if not url or not download_path:
                messagebox.showerror("Error", "URL and download path are required")
                return

            if not self.validate_url(url, is_playlist):
                messagebox.showerror("Error", "Invalid YouTube URL format")
                return

            if not os.path.exists(download_path):
                messagebox.showerror("Error", "Download path does not exist")
                return

            # Update UI state
            self.status_label.configure(text="Initializing download...")
            self.download_button.configure(state="disabled")
            self.progress_bar.set(0)
            self.total_videos = 0
            self.downloaded_videos = 0

            # Update yt-dlp using pip
            self.status_label.configure(text="Checking for updates...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Update failed: {e.output}")

            # Configure download options
            ydl_opts = self.get_ydl_opts(download_path, is_playlist)

            # Start download process
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video information first
                info = ydl.extract_info(url, download=False)
                
                # Set total videos count
                if is_playlist:
                    entries = info.get("entries", [])
                    self.total_videos = len([e for e in entries if e is not None])
                else:
                    self.total_videos = 1

                if self.total_videos == 0:
                    raise Exception("No valid videos found to download")

                self.status_label.configure(text=f"Starting download of {self.total_videos} video(s)...")
                ydl.download([url])

            # Success message
            self.status_label.configure(text="Download Complete!")
            messagebox.showinfo("Success", f"Downloaded {self.total_videos} video(s) to:\n{download_path}")

        except Exception as e:
            self.status_label.configure(text="Error occurred!")
            messagebox.showerror("Error", f"Download failed:\n{str(e)}")

        finally:
            self.reset_ui()

    def reset_ui(self):
        self.download_button.configure(state="normal")
        self.progress_bar.set(0)
        self.status_label.configure(text="Ready to download")

    def progress_hook(self, d):
        try:
            status = d.get('status', '')
            if status == 'started':
                self.window.after(0, lambda: self.status_label.configure(
                    text=f"Starting video {self.downloaded_videos + 1} of {self.total_videos}..."
                ))

            elif status == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total_bytes > 0:
                    percentage = min(downloaded / total_bytes, 1.0)
                    speed = d.get('speed', 0)
                    speed_str = f"{speed/1024/1024:.1f} MB/s" if speed else "N/A"
                    
                    self.window.after(0, lambda: self.progress_bar.set(percentage))
                    self.window.after(0, lambda: self.status_label.configure(
                        text=f"Downloading video {self.downloaded_videos + 1} of {self.total_videos}"
                             f" – {percentage:.1%} @ {speed_str}"
                    ))

            elif status == 'finished':
                self.downloaded_videos += 1
                self.window.after(0, lambda: self.progress_bar.set(1))
                self.window.after(0, lambda: self.status_label.configure(
                    text=f"Completed video {self.downloaded_videos} of {self.total_videos}"
                ))
        except Exception as e:
            print(f"Progress hook error: {str(e)}")

    def get_ydl_opts(self, download_path, is_playlist):
        selected_quality = self.quality_var.get().split()[0][:-1]  # Remove 'p' from quality
        
        output_template = (
            str(Path(download_path) / '%(title)s.%(ext)s') if not is_playlist 
            else str(Path(download_path) / '%(playlist)s' / '%(playlist_index)s - %(title)s.%(ext)s')
        )
        
        return {
            'format': f'bestvideo[height<={selected_quality}]+bestaudio/best[height<={selected_quality}]/best',
            'outtmpl': output_template,
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'ignoreerrors': is_playlist,
            'yes_playlist': is_playlist,
            'merge_output_format': 'mp4',
            'nocheckcertificate': True,
            'socket_timeout': 30,
            'retries': 5,
            'extract_flat': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'prefer_ffmpeg': True,
            'ffmpeg_location': self.get_ffmpeg_path()
        }

    def get_ffmpeg_path(self):
        if sys.platform == 'win32':
            return str(Path(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))) / 'ffmpeg.exe')
        return 'ffmpeg'  # for non-Windows systems

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()
