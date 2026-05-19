@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo =======================================================
echo    Law Office Management System - Professional Build
echo    مكتب المستشار/ أحمد شعبان مجرية للمحاماة
echo =======================================================
echo.

:: Configuration
set APP_NAME=LawOfficeSystem
set DIST_DIR=dist\LawOfficeSystem_Portable
set PYTHON_VER=3.8

:: Check Python version
python --version >python_version.txt 2>&1
set /p PY_VER_STR=<python_version.txt
del python_version.txt
echo [INFO] Python detected: %PY_VER_STR%

echo [1/6] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist %APP_NAME%.spec del %APP_NAME%.spec

echo.
echo [2/6] Installing requirements...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo [3/6] Building EXE with PyInstaller...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "%APP_NAME%" ^
    --icon="assets\icon.ico" ^
    --add-data "pages;pages" ^
    --hidden-import PyQt5.QtPrintSupport ^
    --hidden-import PyQt5.QtSvg ^
    --hidden-import sqlite3 ^
    main.py

if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo [4/6] Preparing Portable Folder...
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
move "dist\%APP_NAME%.exe" "%DIST_DIR%\"

echo.
echo [5/6] Copying Assets and Database...
if not exist "%DIST_DIR%\Archive" mkdir "%DIST_DIR%\Archive"
if not exist "%DIST_DIR%\Backups" mkdir "%DIST_DIR%\Backups"
if exist law_office.db (
    copy law_office.db "%DIST_DIR%\"
) else (
    echo [WARN] law_office.db not found, will be created on first run.
)

if exist README_تشغيل.txt copy README_تشغيل.txt "%DIST_DIR%\"
if exist INSTALL_WINDOWS7.txt copy INSTALL_WINDOWS7.txt "%DIST_DIR%\"

echo.
echo [6/6] Finalizing...
echo.
echo =======================================================
echo [SUCCESS] Build Complete!
echo Location: %DIST_DIR%
echo =======================================================
echo.
echo Default Login:
echo   User: admin
echo   Pass: admin123
echo =======================================================
pause
