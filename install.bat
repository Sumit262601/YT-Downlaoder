@echo off
echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing wheel and setuptools...
python -m pip install --upgrade wheel setuptools

echo Installing YouTube GUI Dependencies...
python -m pip install -r requirements.txt --no-cache-dir

echo Installing Visual Studio Build Tools...
winget install Microsoft.VisualStudio.2022.BuildTools --silent

echo Installation complete!
pause