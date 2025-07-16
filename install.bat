@echo off
echo ==================================================
echo         Installing YouTube Downloader...
echo ==================================================

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [*] Upgrading pip...
python -m pip install --upgrade pip

REM Install required packages
echo [*] Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Download and install FFmpeg if not already present
if not exist "venv\Scripts\ffmpeg.exe" (
    echo [*] FFmpeg not found. Downloading...

    powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"

    powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'temp' -Force"

    move /Y "temp\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" "venv\Scripts\" >nul

    REM Clean up
    rmdir /S /Q temp
    del /Q ffmpeg.zip

    echo [*] FFmpeg installed successfully.
) else (
    echo [*] FFmpeg already exists in venv\Scripts.
)

echo ==================================================
echo        Setup completed successfully!
echo ==================================================
pause
