@echo off
REM ==========================================================
REM  NOVA Player - Compilation complete sous Windows
REM  Double-cliquez sur ce fichier : il installe tout et
REM  genere  dist\NOVA-Player\NOVA-Player.exe  (+ un ZIP)
REM ==========================================================
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [ERREUR] Python 3.10+ est introuvable. Installez-le depuis https://www.python.org
  echo          et cochez "Add python.exe to PATH".
  pause & exit /b 1
)

echo [1/4] Environnement virtuel...
if not exist .venv ( python -m venv .venv || goto :fail )
call .venv\Scripts\activate.bat

echo [2/4] Installation des dependances...
python -m pip install --upgrade pip >nul
pip install -r requirements-build.txt || goto :fail

echo [3/4] Generation de l'icone...
python tools\make_icon.py || goto :fail

echo [4/4] Compilation (PyInstaller)...
pyinstaller --noconfirm --clean --windowed --name NOVA-Player ^
  --icon assets\icon.ico ^
  --exclude-module PySide6.QtQml --exclude-module PySide6.QtQuick ^
  --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtPdf ^
  main.py || goto :fail

powershell -NoProfile -Command "Compress-Archive -Force -Path 'dist\NOVA-Player' -DestinationPath 'dist\NOVA-Player-Windows.zip'"

echo.
echo ===== TERMINE =====
echo Executable : %cd%\dist\NOVA-Player\NOVA-Player.exe
echo Archive    : %cd%\dist\NOVA-Player-Windows.zip
pause
exit /b 0

:fail
echo.
echo [ERREUR] La compilation a echoue. Lisez les messages ci-dessus.
pause
exit /b 1
