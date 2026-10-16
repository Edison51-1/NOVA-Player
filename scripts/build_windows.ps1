$ErrorActionPreference = "Stop"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --windowed --name NOVAPlayer --onedir main.py
if (Test-Path "dist\NOVAPlayer.zip") { Remove-Item "dist\NOVAPlayer.zip" }
Compress-Archive -Path "dist\NOVAPlayer\*" -DestinationPath "dist\NOVAPlayer.zip"
Write-Host ""
Write-Host "Build termine : dist\NOVAPlayer\NOVAPlayer.exe"
Write-Host "Archive : dist\NOVAPlayer.zip"
Write-Host "IMPORTANT : verifier la presence des DLL VLC et du dossier plugins avant distribution."
