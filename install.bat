@echo off
echo Installing YouTube Downloader dependencies...

python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Installation completed!
pause