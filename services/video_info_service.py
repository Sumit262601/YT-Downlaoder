import threading
import yt_dlp
import requests
from PIL import Image, ImageTk
from io import BytesIO
from utils.formatters import Formatter

class VideoInfoService:
    """Service class for fetching video information and thumbnails."""
    
    def __init__(self, callback):
        self.callback = callback
    
    def fetch_video_info(self, url):
        """Fetch video information and thumbnail in a separate thread."""
        thread = threading.Thread(target=self._fetch_info_worker, args=(url,), daemon=True)
        thread.start()
    
    def _fetch_info_worker(self, url):
        """Worker method to fetch video information."""
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
                    video_data = {
                        'title': info.get('title', 'Unknown Title'),
                        'duration': Formatter.format_duration(info.get('duration', 0)),
                        'uploader': info.get('uploader', 'Unknown'),
                        'view_count': Formatter.format_view_count(info.get('view_count', 0)),
                        'thumbnail_url': info.get('thumbnail')
                    }
                    
                    self.callback('success', video_data)
                
        except Exception as e:
            print(f"Error fetching video info: {e}")
            self.callback('error', None)
    
    def load_thumbnail(self, url):
        """Load thumbnail image from URL."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image = image.resize((180, 100), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
        return None