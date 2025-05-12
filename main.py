import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import re
import threading
import yt_dlp
import certifi
import ssl
import time

class YouTubeDownloader:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("HD YouTube Downloader")
        self.window.geometry("800x500")
        self.window.configure(fg_color="#2b2b2b")

        # Title Label
        self.title_label = ctk.CTkLabel(
            self.window, 
            text="HD YouTube Downloader",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=20)

        # URL Entry
        self.url_frame = ctk.CTkFrame(self.window)
        self.url_frame.pack(pady=15, padx=20, fill="x")
        
        self.url_label = ctk.CTkLabel(
            self.url_frame, 
            text="YouTube URL:",
            font=("Arial", 14)
        )
        self.url_label.pack(side="left", padx=10)
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame, 
            width=500,
            height=35,
            placeholder_text="Paste YouTube URL here..."
        )
        self.url_entry.pack(side="left", padx=10)

        # Resolution Options
        self.quality_frame = ctk.CTkFrame(self.window)
        self.quality_frame.pack(pady=15)
        
        self.quality_var = ctk.StringVar(value="1080p")
        resolutions = ["2160p (4K)", "1440p (2K)", "1080p", "720p"]
        
        self.quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="Select Quality:",
            font=("Arial", 14)
        )
        self.quality_label.pack(side="left", padx=10)
        
        self.quality_menu = ctk.CTkOptionMenu(
            self.quality_frame,
            values=resolutions,
            variable=self.quality_var,
            width=150
        )
        self.quality_menu.pack(side="left", padx=10)

        # Download Button
        self.download_button = ctk.CTkButton(
            self.window,
            text="Download Video",
            width=200,
            height=40,
            command=self.download_video,
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
            text="© 2025 Your Company Name | Version 1.0",
            font=("Arial", 10),
            text_color="gray"
        )
        self.publisher_label.pack()

        # Move the original status_label above the publisher info
        self.status_label.pack_forget()
        self.status_label.pack(pady=(5,10))

    def validate_url(self, url):
        """Validate YouTube URL format"""
        youtube_regex = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[A-Za-z0-9_-]{11}.*$'
        return bool(re.match(youtube_regex, url))

    def download_video(self):
        """Starts the download in a separate thread"""
        thread = threading.Thread(target=self.download_video_thread)
        thread.daemon = True  # Thread will close with the main program
        thread.start()

    def download_video_thread(self):
        """Handles the actual download process"""
        try:
            url = self.url_entry.get().strip()
            if not url:
                self.window.after(0, lambda: messagebox.showerror("Error", "Please enter a YouTube URL"))
                return
            
            if not self.validate_url(url):
                self.window.after(0, lambda: messagebox.showerror("Error", "Invalid YouTube URL format"))
                return

            self.window.after(0, lambda: self.status_label.configure(text="Fetching video information..."))
            self.window.after(0, lambda: self.download_button.configure(state="disabled"))

            # Select download path first
            download_path = filedialog.askdirectory(title="Select Download Location")
            if not download_path:
                self.window.after(0, self.reset_ui)
                return

            # Extract numerical resolution value
            selected_quality = self.quality_var.get().split()[0][:-1]  # Gets "2160" from "2160p (4K)"
            
            ydl_opts = {
                'format': f'bestvideo[height<={selected_quality}]+bestaudio/best',
                'format_sort': [
                    'res:2160',
                    'res:1440',
                    'res:1080',
                    'res:720',
                    'fps'
                ],
                'outtmpl': f'{download_path}/%(title)s.%(ext)s',
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
                'ffmpeg_location': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'Scripts', 'ffmpeg.exe')
            }

            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        self.window.after(0, lambda: self.status_label.configure(text="Downloading video..."))
                        info = ydl.extract_info(url, download=True)
                        break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(f"Download failed after {max_retries} attempts: {str(e)}")
                    time.sleep(2)

            self.window.after(0, lambda: self.status_label.configure(text="Download Complete!"))
            self.window.after(0, lambda: messagebox.showinfo("Success", f"Video downloaded successfully to:\n{download_path}"))

        except Exception as e:
            error_msg = str(e)
            self.window.after(0, lambda: self.status_label.configure(text="Error occurred!"))
            self.window.after(0, lambda: messagebox.showerror("Error", f"Download failed: {error_msg}"))
        
        finally:
            self.window.after(0, self.reset_ui)

    def reset_ui(self):
        """Reset UI elements after download"""
        self.window.after(0, lambda: self.download_button.configure(state="normal"))
        self.window.after(0, lambda: self.progress_bar.set(0))
        self.window.after(0, lambda: self.status_label.configure(text="Ready"))

    def progress_hook(self, d):
        """Handle download progress updates"""
        if d['status'] == 'downloading':
            try:
                total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total_bytes:
                    percentage = downloaded / total_bytes
                    self.window.after(0, lambda: self.progress_bar.set(percentage))
                    self.window.after(0, lambda: self.status_label.configure(
                        text=f"Downloaded: {percentage:.1%}"
                    ))
            except:
                pass

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()