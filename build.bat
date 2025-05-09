@echo off
pip install -r requirements.txt
pyinstaller --onefile --windowed --icon=your_icon.ico --name=YoutubeDownloader main.py