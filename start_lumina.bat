@echo off
echo ===================================================
echo   Starting Lumina AI...
echo ===================================================

echo [1/3] Starting Backend Server...
start "Lumina Backend" cmd /k "cd backend && python -m uvicorn main:app --reload"

echo [2/3] Starting Frontend Server...
start "Lumina Frontend" cmd /k "cd frontend && npm run dev"

echo [3/3] Waiting for servers to initialize (5 seconds)...
timeout /t 5 /nobreak >nul

echo ===================================================
echo   Opening Lumina in Browser...
echo ===================================================
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:5173 (or 5174 if busy)
echo ===================================================

:: Try to open the default port
start http://localhost:5173
