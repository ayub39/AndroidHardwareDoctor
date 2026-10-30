@echo off
title Android Hardware Doctor - USB Diagnostic Tool
cd /d "%~dp0"

:: Prioritize clean local platform-tools in bin directory
if exist "%~dp0bin" (
    set "PATH=%~dp0bin;%PATH%"
)

:: Add Android SDK platform-tools to session PATH as fallback
if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools" (
    set "PATH=%PATH%;%LOCALAPPDATA%\Android\Sdk\platform-tools"
)

echo ========================================================
echo   Starting Android Hardware Doctor...
echo ========================================================
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Gagal menjalankan aplikasi! Pastikan Python dan dependensi terpasang.
    pause
)
