@echo off
echo ========================================
echo  HCAT - AI Project Management System
echo ========================================
echo.
echo Starting all services...
echo.

REM Start Mock Backend (port 3000)
echo [1/3] Starting Mock Backend...
start "HCAT - Mock Backend" cmd /k "cd C:\Users\tejas\Desktop\HCAT-main\ai-backend\tests && C:\Users\tejas\Desktop\HCAT-main\.venv\Scripts\python.exe mock_server.py"
timeout /t 3 /nobreak >nul

REM Start AI Backend (port 8000)
echo [2/3] Starting AI Backend...
start "HCAT - AI Backend" cmd /k "cd C:\Users\tejas\Desktop\HCAT-main\ai-backend && C:\Users\tejas\Desktop\HCAT-main\.venv\Scripts\python.exe start.py"
timeout /t 3 /nobreak >nul

REM Start Frontend (port 5173)
echo [3/3] Starting Frontend...
start "HCAT - Frontend" cmd /k "cd C:\Users\tejas\Desktop\HCAT-main\frontend && npm run dev"
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo  All services started successfully!
echo ========================================
echo.
echo Services running at:
echo  - Mock Backend:  http://localhost:3000
echo  - AI Backend:    http://localhost:8000
echo  - Frontend:      http://localhost:5173
echo.
echo Opening frontend in your browser...
echo.
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo Press any key to stop all services...
pause >nul

REM Close all terminal windows
taskkill /FI "WindowTitle eq HCAT - Mock Backend" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq HCAT - AI Backend" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq HCAT - Frontend" /T /F >nul 2>&1

echo.
echo All services stopped.
echo.
pause
