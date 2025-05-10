@echo off
echo Setting up YouTube Downloader...

@echo off
echo Create and activate virtual environment
python -m venv venv
call venv\Scripts\activate.bat

@echo off
echo Install requirements and update yt-dlp
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install --upgrade yt-dlp

echo Installation completed!
pause