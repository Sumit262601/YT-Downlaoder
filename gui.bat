@echo off
echo Starting YouTube GUI...

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please run install.bat first.
    pause
    exit
)

REM Run the application
python main.py

REM Deactivate virtual environment
deactivate

pause