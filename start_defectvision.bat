@echo off
echo ===================================================
echo   DefectVision AI -- Production Full-Stack Launcher
echo ===================================================
echo.
echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "DefectVision AI - FastAPI Backend" cmd /k "cd /d %~dp0DefectVisionAI && set KMP_DUPLICATE_LIB_OK=TRUE && python -m uvicorn app:app --host 127.0.0.1 --port 8000"

echo [2/2] Launching Vite React Frontend on http://127.0.0.1:5173 ...
start "DefectVision AI - Vite Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Application initialized!
echo Open your browser at: http://127.0.0.1:5173
echo ===================================================
pause
