python -m venv venv
call venv\Scripts\activate

echo Installing/Updating dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

@REM echo Updating yt-dlp with force reinstall...
@REM python -m pip uninstall -y yt-dlp
@REM python -m pip install --no-cache-dir -U yt-dlp

echo Installation completed!
pause