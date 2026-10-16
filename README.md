# NOVA Player

Lecteur multimédia de bureau multiplateforme (Windows et Linux), interface sombre premium.
Cette première version fournit une base fonctionnelle extensible : ouverture de fichiers, lecture/pause,
arrêt, navigation dans la playlist, barre de progression, volume, plein écran et playlist locale.

## Prérequis
- Python 3.10 à 3.12 recommandé
- VLC Media Player installé (libVLC doit être disponible sur le système)
- Python packages : `PySide6`, `python-vlc`

> Pour la distribution, respecter les licences de VLC/libVLC et des composants Qt. Le build PyInstaller
> ne garantit pas à lui seul que les bibliothèques natives VLC sont présentes : suivre les instructions ci-dessous.

## Démarrer en développement

### Windows (PowerShell)
```powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```
Installez VLC 64 bits depuis le site officiel de VideoLAN avant de lancer l'application.

### Linux (Debian, Ubuntu, Kali)
```bash
sudo apt update
sudo apt install python3-venv vlc libvlc5 libvlc-dev
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```
Si `python-vlc` ne trouve pas libVLC, vérifiez que `libvlc.so` est disponible via le gestionnaire de paquets.

## Créer l'exécutable Windows (.exe)
Sur Windows, dans PowerShell :
```powershell
.\scripts\build_windows.ps1
```
Le résultat attendu est `dist\NOVAPlayer\NOVAPlayer.exe` (dossier de distribution).
Le script crée aussi une archive ZIP de ce dossier. Le build doit être réalisé sur Windows.

### Installateur Windows
Installez Inno Setup, puis ouvrez `installer\NOVAPlayer.iss` dans Inno Setup et compilez.
Le script Inno Setup suppose que le dossier `dist\NOVAPlayer` existe.
Copiez les DLL de libVLC et le dossier `plugins` de l'installation VLC dans `dist\NOVAPlayer\vlc\` si nécessaire,
puis vérifiez le build sur un Windows propre.

## Créer un paquet Linux
Sur Linux :
```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```
Cela crée une distribution PyInstaller dans `dist/NOVAPlayer/` et une archive `.tar.gz`.
Ce n'est pas un AppImage autonome : libVLC et ses plugins peuvent nécessiter une installation système.
Le build Linux doit être réalisé sur Linux.

## Formats
Les formats lisibles dépendent des codecs installés dans VLC. Les formats courants pris en charge comprennent
MP4, MKV, AVI, MOV, WebM, MP3, WAV, FLAC et AAC.

## Limites connues de cette version initiale
- Les métadonnées, pochettes, égaliseur graphique avancé, sous-titres configurables et notifications système
  sont prévus pour les versions suivantes.
- Tester impérativement les builds sur les machines cibles avant de distribuer.


## Compilation Windows sans PC Windows local
Le fichier `.github/workflows/build-windows.yml` décrit un build Windows x64 sur un runner Windows GitHub Actions.
Pour l'utiliser, il faut créer un dépôt GitHub, y téléverser le contenu de ce projet, puis lancer
**Actions → Build NOVA Player for Windows → Run workflow**. À la fin, télécharger l'artifact
`NOVAPlayer-Windows-x64` depuis le run. Cela nécessite un compte GitHub et une action manuelle.
Le workflow produit une archive de distribution, pas un installateur Inno Setup signé.
Il faut tester l'application sur un PC Windows avant de la distribuer.
