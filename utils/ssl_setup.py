import ssl
import certifi

def setup_ssl():
    """Configure SSL certificates for secure connections."""
    ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())