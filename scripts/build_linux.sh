#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m PyInstaller --noconfirm --clean --windowed --name NOVAPlayer --onedir main.py
tar -czf dist/NOVAPlayer-linux.tar.gz -C dist NOVAPlayer
echo "Build termine : dist/NOVAPlayer/"
echo "Archive : dist/NOVAPlayer-linux.tar.gz"
echo "IMPORTANT : libVLC et ses plugins peuvent devoir etre installes sur la machine cible."
