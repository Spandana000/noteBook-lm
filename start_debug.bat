@echo off
echo ===================================================
echo   Lumina DEBUG Mode
echo ===================================================
echo.
echo [1/2] Stopping old processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
echo Done.
echo.

echo [2/3] Starting Backend (DEBUG)...
start "Lumina Backend DEBUG" cmd /k "cd backend && set PYTHONPATH=. && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo [3/3] Starting Frontend...
start "Lumina Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo DEBUG MODE ACTIVE. Check the "Lumina Backend DEBUG" window for errors!
pause
