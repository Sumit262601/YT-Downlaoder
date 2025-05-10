@echo off
echo Installing YouTube Downloader dependencies...

REM Create and activate virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Update pip and yt-dlp
python -m pip install --upgrade pip
python -m pip install --upgrade yt-dlp --force-reinstall

REM Install other requirements
python -m pip install customtkinter pillow certifi

echo Installation completed!
pause