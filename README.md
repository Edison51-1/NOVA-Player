# NOVA Player

Lecteur audio & vidéo moderne — *YOUR MEDIA. YOUR SPACE.*
Python · PySide6 (Qt 6 + FFmpeg) · Windows & Linux.

## Fonctions
- Lecture vidéo (MP4, MKV, AVI, MOV, WEBM…) et audio (MP3, FLAC, WAV, OGG, M4A…)
- Playlist avec miniatures, durées, favoris, ajout / retrait / vidage
- Import de fichiers, de dossiers entiers, glisser-déposer, « Ouvrir avec »
- Barre de progression cliquable, volume, muet, plein écran
- Bibliothèque mémorisée entre deux lancements

## Raccourcis
`Espace` lecture/pause · `←/→` ±5 s · `↑/↓` volume · `M` muet · `F`/`F11` plein écran · `Échap` quitter le plein écran · `N`/`P` suivant/précédent · `Ctrl+O` ajouter

## Lancer depuis les sources
```bash
pip install -r requirements.txt
python main.py
```

## Compiler l'exécutable
- **Windows** : double-cliquez sur `build.bat` → `dist\NOVA-Player\NOVA-Player.exe`
- **Linux** : `./build.sh` → `dist/NOVA-Player/NOVA-Player`

## Obtenir l'exécutable via GitHub (sans rien installer)
1. Poussez le projet sur GitHub (branche `main`).
2. Onglet **Actions** → workflow *Build NOVA Player* → téléchargez l'artefact `NOVA-Player-Windows`.
3. Pour une release publique : `git tag v1.0.0 && git push origin v1.0.0`
   → le ZIP Windows et l'archive Linux sont attachés à la release.
