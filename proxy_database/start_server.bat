@echo off
echo Starting Proxy User Management System...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python proxy-sync.py