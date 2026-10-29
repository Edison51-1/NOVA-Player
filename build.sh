#!/usr/bin/env bash
# NOVA Player - compilation complète sous Linux (lancer : ./build.sh)
# Génère dist/NOVA-Player/NOVA-Player  + dist/NOVA-Player-Linux.tar.gz
set -euo pipefail
cd "$(dirname "$0")"

command -v python3 >/dev/null || { echo "Python 3.10+ requis (sudo apt install python3 python3-venv)"; exit 1; }

echo "[1/4] Environnement virtuel..."
[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "[2/4] Dépendances..."
python -m pip install --upgrade pip >/dev/null
pip install -r requirements-build.txt

echo "[3/4] Icône..."
python tools/make_icon.py

echo "[4/4] Compilation (PyInstaller)..."
pyinstaller --noconfirm --clean --windowed --name NOVA-Player \
  --icon assets/icon.png \
  --exclude-module PySide6.QtQml --exclude-module PySide6.QtQuick \
  --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtPdf \
  main.py

tar -C dist -czf dist/NOVA-Player-Linux.tar.gz NOVA-Player
echo
echo "===== TERMINÉ ====="
echo "Exécutable : $(pwd)/dist/NOVA-Player/NOVA-Player"
echo "Archive    : $(pwd)/dist/NOVA-Player-Linux.tar.gz"
