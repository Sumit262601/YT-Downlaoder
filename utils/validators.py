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
        """Checks if the URL is a playlist URL - Enhanced detection."""
        playlist_indicators = [
            "playlist?list=",
            "/playlist/",
            "&list=",  # Video URL with playlist parameter
            "?list=",  # Direct playlist parameter
        ]
        
        # Convert to lowercase for case-insensitive matching
        url_lower = url.lower()
        
        return any(indicator in url_lower for indicator in playlist_indicators)
    
    @staticmethod
    def is_single_video(url):
        """Checks if URL is specifically a single video (not playlist)."""
        if not URLValidator.validate_url(url):
            return False
        
        # If it contains playlist indicators, it's not a single video
        if URLValidator.is_playlist(url):
            return False
        
        # Check for single video patterns
        single_video_patterns = [
            r'youtube\.com/watch\?v=[A-Za-z0-9_-]{11}$',  # Standard video URL
            r'youtu\.be/[A-Za-z0-9_-]{11}$',  # Short URL
            r'youtube\.com/watch\?v=[A-Za-z0-9_-]{11}&',  # With other params (not list)
        ]
        
        return any(re.search(pattern, url) for pattern in single_video_patterns)