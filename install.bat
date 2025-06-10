@echo off
echo Installing YouTube Downloader...

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Upgrade all pip scripts versions
echo Upgrading pip...
%VIRTUAL_ENV%\Scripts\python.exe -m pip install --upgrade pip

REM Install required packages
pip install -r requirements.txt

REM Download FFmpeg if not exists in venv\Scripts
if not exist "venv\Scripts\ffmpeg.exe" (
    echo Downloading FFmpeg...
    powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"
    powershell -Command "$ProgressPreference = 'SilentlyContinue'; Expand-Archive -Force 'ffmpeg.zip' -DestinationPath 'temp'"
    move /Y "temp\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" "venv\Scripts\" >nul
    rmdir /S /Q temp
    del /Q ffmpeg.zip
    echo FFmpeg installed successfully.
) else (
    echo FFmpeg already installed.
)

echo Setup completed successfully!
pause