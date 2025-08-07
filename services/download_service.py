import os
import time
import threading
import yt_dlp
from tkinter import messagebox

class DownloadService:
    """Service class for handling YouTube downloads."""
    
    def __init__(self, progress_callback, status_callback, completion_callback):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.completion_callback = completion_callback
        self.current_video_index = 0
        self.total_playlist_videos = 0
    
    def start_download(self, url, download_path, download_type, media_type, quality_selection):
        """Start download in a separate thread."""
        thread = threading.Thread(
            target=self._download_worker, 
            args=(url, download_path, download_type, media_type, quality_selection),
            daemon=True
        )
        thread.start()
    
    def _download_worker(self, url, download_path, download_type, media_type, quality_selection):
        """Worker method for downloading content."""
        try:
            self.status_callback("Fetching information...")
            
            format_options = self._get_format_options(media_type, quality_selection)
            
            ydl_opts = {
                'progress_hooks': [self._progress_hook],
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
            
            ydl_opts.update(format_options)
            
            # Set output template and get playlist info if needed
            file_ext = format_options.get('outtmpl_ext', 'mp4')
            if download_type == "playlist":
                self._setup_playlist_download(url, download_path, file_ext, ydl_opts)
            else:
                self._setup_single_download(download_path, file_ext, ydl_opts)
            
            # Perform download with retries
            self._perform_download(url, ydl_opts)
            
            self.status_callback("Download Complete!")
            self.completion_callback("success", f"Content downloaded successfully to:\n{download_path}")
            
        except Exception as e:
            error_msg = str(e)
            self.status_callback("Error occurred!")
            self.completion_callback("error", f"Download failed: {error_msg}")
    
    def _setup_playlist_download(self, url, download_path, file_ext, ydl_opts):
        """Setup options for playlist download."""
        self.status_callback("Fetching playlist info...")
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
    
    def _setup_single_download(self, download_path, file_ext, ydl_opts):
        """Setup options for single video download."""
        ydl_opts['outtmpl'] = os.path.join(download_path, f'%(title)s.{file_ext}')
        self.total_playlist_videos = 1
        self.current_video_index = 0
    
    def _perform_download(self, url, ydl_opts):
        """Perform the actual download with retry logic."""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.status_callback("Downloading...")
                    info = ydl.extract_info(url, download=True)
                    break
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"Download failed after {max_retries} attempts: {str(e)}")
                time.sleep(2)
    
    def _get_format_options(self, media_type, quality_selection):
        """Get yt-dlp format options based on media type and quality."""
        if media_type == "Audio Only":
            return self._get_audio_format_options(quality_selection)
        else:
            return self._get_video_format_options(quality_selection)
    
    def _get_audio_format_options(self, quality_selection):
        """Get audio format options."""
        format_map = {
            "MP3 (128kbps)": {'codec': 'mp3', 'quality': '128', 'ext': 'mp3'},
            "MP3 (320kbps)": {'codec': 'mp3', 'quality': '320', 'ext': 'mp3'},
            "WAV": {'codec': 'wav', 'ext': 'wav'},
            "M4A": {'codec': 'm4a', 'ext': 'm4a'}
        }
        
        format_info = format_map.get(quality_selection, format_map["MP3 (128kbps)"])
        
        postprocessor = {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format_info['codec'],
        }
        
        if 'quality' in format_info:
            postprocessor['preferredquality'] = format_info['quality']
        
        return {
            'format': 'bestaudio/best',
            'postprocessors': [postprocessor],
            'outtmpl_ext': format_info['ext']
        }
    
    def _get_video_format_options(self, quality_selection):
        """Get video format options."""
        selected_quality = quality_selection.split()[0][:-1]  # Gets "2160" from "2160p (4K)"
        return {
            'format': f'bestvideo[height<={selected_quality}]+bestaudio/best',
            'format_sort': ['res:2160', 'res:1440', 'res:1080', 'res:720', 'fps'],
            'merge_output_format': 'mp4',
            'outtmpl_ext': 'mp4'
        }
    
    def _progress_hook(self, d):
        """Handle download progress updates."""
        if d['status'] == 'downloading':
            try:
                total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                percentage = 0
                if total_bytes:
                    percentage = downloaded / total_bytes
                
                self.progress_callback(percentage)
                
                # Update status with playlist progress if applicable
                status_text = self._get_download_status_text(d, percentage, total_bytes)
                self.status_callback(status_text)
                
            except Exception:
                self.status_callback("Downloading... (progress update error)")
        
        elif d['status'] == 'finished':
            self.progress_callback(1.0)
            media_type = getattr(self, '_current_media_type', 'Video')
            if media_type == "Audio Only":
                self.status_callback("Converting to audio format...")
            else:
                self.status_callback("Processing and merging files...")
    
    def _get_download_status_text(self, d, percentage, total_bytes):
        """Generate status text for download progress."""
        status_text = ""
        
        if self.total_playlist_videos > 1:
            if d.get('info_dict', {}).get('playlist_index') is not None:
                self.current_video_index = d['info_dict']['playlist_index']
            
            display_current_index = max(1, self.current_video_index)
            status_text = f"Downloading item {display_current_index} of {self.total_playlist_videos}: "
        
        if total_bytes:
            status_text += f"Downloaded: {percentage:.1%} of {d.get('_total_bytes_str', 'N/A')}"
        else:
            status_text += f"Downloaded: {d.get('_downloaded_bytes_str', 'N/A')}"
        
        return status_text