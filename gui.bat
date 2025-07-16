@echo off
echo ==================================================
echo             Starting YouTube GUI...
echo ==================================================

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit
)

REM Upgrade pip
echo ==================================================
echo             Upgrading pip...
echo ==================================================
python -m pip install --upgrade pip

REM Upgrade libraries
echo ==================================================
echo             Upgrading libraries from requirements.txt...
echo ==================================================
pip install --upgrade -r requirements.txt

REM Freeze current installed packages to requirements.txt
echo ==================================================
echo            Updating requirements.txt with current versions...
echo ==================================================

REM Run the main Python application
echo ==================================================
echo            Running the application...
echo ==================================================
python main.py

REM Deactivate virtual environment
echo ==================================================
echo            Deactivating virtual environment...
echo ==================================================
deactivate

pause
