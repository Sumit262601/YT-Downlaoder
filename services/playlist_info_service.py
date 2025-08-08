import threading
import yt_dlp
from utils.validators import URLValidator

class PlaylistInfoService:
    """Service for fetching playlist information and video lists."""
    
    def __init__(self, callback):
        self.callback = callback
    
    def fetch_playlist_info(self, url):
        """Fetch playlist information in a separate thread."""
        if not URLValidator.is_playlist(url):
            self.callback('error', "Not a playlist URL", None, None)
            return
        
        thread = threading.Thread(target=self._fetch_playlist_worker, args=(url,), daemon=True)
        thread.start()
    
    def _fetch_playlist_worker(self, url):
        """Worker method to fetch playlist information."""
        try:
            print(f"PlaylistInfoService: Fetching playlist info for {url}")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,  # Get detailed info for each video
                'nocheckcertificate': True,
                'ignoreerrors': True,  # Skip unavailable videos
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    self.callback('error', "Could not fetch playlist information", None, None)
                    return
                
                if info.get('_type') != 'playlist':
                    self.callback('error', "URL is not a playlist", None, None)
                    return
                
                # Extract playlist metadata
                playlist_info = {
                    'title': info.get('title', 'Unknown Playlist'),
                    'uploader': info.get('uploader', 'Unknown Channel'),
                    'description': info.get('description', ''),
                    'entries': info.get('entries', [])
                }
                
                # Process video entries
                video_list = []
                for i, entry in enumerate(playlist_info['entries']):
                    if entry:  # Skip None entries (unavailable videos)
                        video_data = {
                            'id': entry.get('id', ''),
                            'title': entry.get('title', f'Video {i+1}'),
                            'duration': entry.get('duration', 0),
                            'view_count': entry.get('view_count', 0),
                            'uploader': entry.get('uploader', ''),
                            'upload_date': entry.get('upload_date', ''),
                            'url': entry.get('webpage_url', entry.get('url', '')),
                            'thumbnail': entry.get('thumbnail', ''),
                            'playlist_index': i + 1
                        }
                        video_list.append(video_data)
                
                print(f"PlaylistInfoService: Found {len(video_list)} videos in playlist")
                self.callback('success', None, playlist_info, video_list)
                
        except Exception as e:
            print(f"PlaylistInfoService: Error fetching playlist info: {e}")
            self.callback('error', f"Error fetching playlist: {str(e)}", None, None)