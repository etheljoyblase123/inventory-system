@echo off
echo Starting Inventory Management System...
echo.

:: Check if requirements are installed
echo Installing/Updating dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Please check your internet connection and python/pip installation.
    pause
    exit /b %errorlevel%
)

echo.
echo Launching Application...
python app.py
if %errorlevel% neq 0 (
    echo [ERROR] Application crashed or failed to start.
    pause
)

pause
