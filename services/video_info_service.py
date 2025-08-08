import threading
import yt_dlp
import requests
from PIL import Image, ImageTk
from io import BytesIO
from utils.formatters import Formatter
from utils.validators import URLValidator

class VideoInfoService:
    """Service class for fetching video information and thumbnails."""
    
    def __init__(self, callback):
        self.callback = callback
        self._current_request_url = None  # Track current request
    
    def fetch_video_info(self, url):
        """Fetch video information and thumbnail in a separate thread."""
        # Double-check that this is not a playlist before proceeding
        if URLValidator.is_playlist(url):
            print(f"VideoInfoService: Refusing to fetch info for playlist URL: {url}")
            self.callback('error', None)
            return
        
        # Cancel any existing request
        self._current_request_url = url
        
        thread = threading.Thread(target=self._fetch_info_worker, args=(url,), daemon=True)
        thread.start()
    
    def _fetch_info_worker(self, url):
        """Worker method to fetch video information."""
        # Check if this request is still valid (not superseded by a newer one)
        if self._current_request_url != url:
            print(f"VideoInfoService: Request for {url} cancelled (superseded)")
            return
        
        try:
            print(f"VideoInfoService: Fetching info for {url}")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'nocheckcertificate': True,
                'playlist_items': '1',  # Only get first item if somehow a playlist
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Additional check: if this returned playlist info, reject it
                if info and info.get('_type') == 'playlist':
                    print(f"VideoInfoService: Received playlist info for {url}, rejecting")
                    self.callback('error', None)
                    return
                
                if info:
                    print(f"VideoInfoService: Successfully got info for: {info.get('title', 'Unknown')}")
                    
                    video_data = {
                        'title': info.get('title', 'Unknown Title'),
                        'duration': Formatter.format_duration(info.get('duration', 0)),
                        'uploader': info.get('uploader', 'Unknown'),
                        'view_count': Formatter.format_view_count(info.get('view_count', 0)),
                        'thumbnail_url': info.get('thumbnail')
                    }
                    
                    # Final check that this request is still current
                    if self._current_request_url == url:
                        self.callback('success', video_data)
                    else:
                        print(f"VideoInfoService: Info ready for {url} but request was superseded")
                
        except Exception as e:
            print(f"VideoInfoService: Error fetching video info for {url}: {e}")
            if self._current_request_url == url:
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