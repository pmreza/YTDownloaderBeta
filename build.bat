@echo off
echo ==============================================
echo INFINITE DOWNLOADER - Build Script
echo ==============================================

echo 1. Cleaning old builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q INFINITE_DOWNLOADER.spec 2>nul
del /q "C:\Users\helloWorld\Desktop\INFINITE_DOWNLOADER.exe" 2>nul

echo.
echo 2. Running PyInstaller...
pyinstaller --noconfirm --onefile --windowed --icon=logo.ico --paths . --add-data "src/ui/index.html;src/ui" --add-data "src/ui/style.css;src/ui" --add-data "src/ui/script.js;src/ui" --add-data "src/ui/animation.js;src/ui" --hidden-import "src.ui.app_window" --hidden-import "src.core.downloader" --hidden-import "src.core.deps_manager" --name "INFINITE_DOWNLOADER" --distpath "C:\Users\helloWorld\Desktop" src/main.py

echo.
echo ==============================================
echo Build Complete! Check your Desktop for INFINITE_DOWNLOADER.exe
echo ==============================================
pause
