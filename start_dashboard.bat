@echo off
echo 🚀 Starting Crypto Trading Bot Dashboard...
echo 📊 Dashboard will open in your browser at http://localhost:8501
echo 🔴 Press Ctrl+C to stop the dashboard
echo ============================================================

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Launch the dashboard
python launch_dashboard.py

pause
