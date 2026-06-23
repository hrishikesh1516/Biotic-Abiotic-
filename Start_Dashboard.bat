@echo off
title Paleobiology Dashboard Launcher
echo ==================================================
echo Starting Paleobiology Dashboard Engines...
echo ==================================================

echo [1/3] Starting Python Data Engine (Port 8080)...
start /B conda run -n geo_env uvicorn server:app --port 8080

echo [2/3] Starting React Web Interface...
cd interactive-dashboard
start /B conda run -n geo_env npm run dev

echo [3/3] Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

echo Opening Dashboard in your browser...
start http://localhost:5173

echo.
echo Both engines are running in the background.
echo To close the engines later, simply close this command window.
pause
