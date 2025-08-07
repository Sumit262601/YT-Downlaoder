import os
import customtkinter as ctk
from components.main_window import MainWindow
from utils.ssl_setup import setup_ssl

def main():
    """Main entry point for the YouTube Downloader application."""
    # Setup SSL certificates
    setup_ssl()
    
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run the application
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()