import os
import time
import threading
import yt_dlp
from tkinter import messagebox


class DownloadService:
    """Enhanced download service with playlist and single video support."""

    def __init__(self, progress_callback, status_callback, completion_callback):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.completion_callback = completion_callback
        self.current_video_index = 0
        self.total_playlist_videos = 0

    def start_download(self, url, download_path, download_type, media_type, quality_selection):
        """Start regular download in a separate thread."""
        thread = threading.Thread(
            target=self._download_worker,
            args=(url, download_path, download_type, media_type, quality_selection),
            daemon=True
        )
        thread.start()

    def start_playlist_download(self, selected_videos, download_path, media_type, quality_selection):
        """Start playlist download for selected videos."""
        thread = threading.Thread(
            target=self._playlist_download_worker,
            args=(selected_videos, download_path, media_type, quality_selection),
            daemon=True
        )
        thread.start()

    def _playlist_download_worker(self, selected_videos, download_path, media_type, quality_selection):
        """Worker method for downloading selected playlist videos."""
        try:
            self.status_callback("Preparing playlist download...")
            self.total_playlist_videos = len(selected_videos)
            self.current_video_index = 0
            format_options = self._get_format_options(media_type, quality_selection)

            playlist_folder = os.path.join(download_path, "Playlist_Download")
            os.makedirs(playlist_folder, exist_ok=True)

            successful_downloads = 0
            failed_downloads = []

            for i, video in enumerate(selected_videos):
                self.current_video_index = i + 1
                video_url = video.get('url', '')
                video_title = video.get('title', f'Video_{i+1}')
                file_ext = format_options.get('outtmpl_ext', 'mp4')
                outtmpl = os.path.join(playlist_folder, f"{video_title}.{file_ext}")
                format_options['outtmpl'] = outtmpl

                try:
                    self.status_callback(f"Downloading: {video_title} ({self.current_video_index}/{self.total_playlist_videos})")
                    self._perform_download(video_url, format_options)
                    successful_downloads += 1
                except Exception as e:
                    failed_downloads.append(f"{video_title} - {str(e)}")

            summary = f"Downloaded: {successful_downloads} / {self.total_playlist_videos}"
            if failed_downloads:
                summary += f"\nFailed: {len(failed_downloads)}\n" + "\n".join(failed_downloads)

            self.completion_callback("success", summary)

        except Exception as e:
            self.status_callback("Error occurred!")
            self.completion_callback("error", f"Playlist download failed: {str(e)}")

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

            file_ext = format_options.get('outtmpl_ext', 'mp4')
            if download_type == "playlist":
                self._setup_playlist_download(url, download_path, file_ext, ydl_opts)
            else:
                self._setup_single_download(download_path, file_ext, ydl_opts)

            self._perform_download(url, ydl_opts)

            self.status_callback("Download Complete!")
            self.completion_callback("success", f"Downloaded to:\n{download_path}")

        except Exception as e:
            self.status_callback("Error occurred!")
            self.completion_callback("error", f"Download failed: {str(e)}")

    def _setup_playlist_download(self, url, download_path, file_ext, ydl_opts):
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
        ydl_opts['outtmpl'] = os.path.join(download_path, f'%(title)s.{file_ext}')
        self.total_playlist_videos = 1
        self.current_video_index = 0

    def _perform_download(self, url, ydl_opts):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.status_callback("Downloading...")
                    ydl.extract_info(url, download=True)
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Download failed after {max_retries} attempts: {str(e)}")
                time.sleep(2)

    def _get_format_options(self, media_type, quality_selection):
        if media_type == "Audio Only":
            return self._get_audio_format_options(quality_selection)
        return self._get_video_format_options(quality_selection)

    def _get_audio_format_options(self, quality_selection):
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
        selected_quality = quality_selection.split()[0][:-1]  # "2160" from "2160p (4K)"
        return {
            'format': f'bestvideo[height<={selected_quality}]+bestaudio/best',
            'format_sort': ['res:2160', 'res:1440', 'res:1080', 'res:720', 'fps'],
            'merge_output_format': 'mp4',
            'outtmpl_ext': 'mp4'
        }

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)

                percentage = downloaded / total_bytes if total_bytes else 0
                self.progress_callback(percentage)

                status_text = self._get_download_status_text(d, percentage, total_bytes)
                self.status_callback(status_text)

            except Exception:
                self.status_callback("Downloading... (progress update error)")

        elif d['status'] == 'finished':
            self.progress_callback(1.0)
            if getattr(self, '_current_media_type', 'Video') == "Audio Only":
                self.status_callback("Converting to audio format...")
            else:
                self.status_callback("Processing and merging files...")

    def _get_download_status_text(self, d, percentage, total_bytes):
        status_text = ""
        if self.total_playlist_videos > 1:
            playlist_index = d.get('info_dict', {}).get('playlist_index')
            if playlist_index is not None:
                self.current_video_index = playlist_index
            status_text += f"Downloading item {self.current_video_index} of {self.total_playlist_videos}: "
        if total_bytes:
            status_text += f"Downloaded: {percentage:.1%} of {d.get('_total_bytes_str', 'N/A')}"
        else:
            status_text += f"Downloaded: {d.get('_downloaded_bytes_str', 'N/A')}"
        return status_text
