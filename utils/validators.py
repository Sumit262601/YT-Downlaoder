import re

class URLValidator:
    """Utility class for validating YouTube URLs."""
    
    @staticmethod
    def validate_url(url):
        """Validate YouTube URL format for both videos and playlists."""
        video_regex = r'^(https?://)?(www\.)?(m\.)?(youtube\.com/watch\?v=|youtu\.be/)[A-Za-z0-9_-]{11}.*$'
        playlist_regex = r'^(https?://)?(www\.)?(m\.)?(youtube\.com/playlist\?list=)[A-Za-z0-9_-]+.*$'
        
        return bool(re.match(video_regex, url) or re.match(playlist_regex, url))
    
    @staticmethod
    def is_playlist(url):
        """Checks if the URL is a playlist URL."""
        return "playlist?list=" in url or "/playlist/" in url