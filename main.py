import os
import sys
from pathlib import Path

# On Windows, tell libVLC where VLC is installed when it is in the standard location.
if sys.platform.startswith("win"):
    app_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    candidates = [
        app_dir / "vlc",
        Path(os.environ.get("ProgramFiles", r"C:\\Program Files")) / "VideoLAN" / "VLC",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\\Program Files (x86)")) / "VideoLAN" / "VLC",
    ]
    for candidate in candidates:
        if (candidate / "libvlc.dll").exists() or candidate.name == "VLC" and candidate.exists():
            try:
                os.add_dll_directory(str(candidate))
                os.environ["PATH"] = str(candidate) + os.pathsep + os.environ.get("PATH", "")
                plugin_dir = candidate / "plugins"
                if plugin_dir.exists():
                    os.environ["VLC_PLUGIN_PATH"] = str(plugin_dir)
            except (AttributeError, OSError):
                pass
            break

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QSlider, QFrame, QMessageBox,
    QSplitter, QToolButton, QStyle
)

try:
    import vlc
except Exception as exc:
    vlc = None
    VLC_IMPORT_ERROR = str(exc)
else:
    VLC_IMPORT_ERROR = ""


APP_NAME = "NOVA Player"
SUPPORTED = "Videos (*.mp4 *.mkv *.avi *.mov *.webm *.mpeg *.mpg *.m4v);;Audio (*.mp3 *.wav *.flac *.aac *.ogg *.m4a *.wma);;Tous les fichiers (*)"


STYLESHEET = """
QMainWindow, QWidget { background: #10131a; color: #eef2f8; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 10pt; }
QFrame#Sidebar, QFrame#Topbar, QFrame#ControlPanel, QFrame#PlaylistPanel { background: #171b25; border: 1px solid #262d3b; border-radius: 14px; }
QLabel#Brand { font-size: 21pt; font-weight: 800; color: #f5f7fb; letter-spacing: 1px; }
QLabel#Accent { color: #8b7cff; font-weight: 700; }
QLabel#Muted { color: #929bad; }
QPushButton, QToolButton { background: #252c3a; color: #f3f5fa; border: 1px solid #343d4e; border-radius: 9px; padding: 9px 13px; }
QPushButton:hover, QToolButton:hover { background: #343d50; border-color: #7166e8; }
QPushButton#Primary { background: #7467f0; border: 0; font-weight: 700; }
QPushButton#Primary:hover { background: #897fff; }
QPushButton#Round { border-radius: 20px; min-width: 36px; min-height: 36px; padding: 4px; }
QListWidget { background: #11151d; border: 0; border-radius: 10px; padding: 5px; outline: 0; }
QListWidget::item { padding: 11px 9px; border-radius: 7px; color: #c8cfdd; }
QListWidget::item:selected { background: #302c55; color: #ffffff; }
QSlider::groove:horizontal { height: 5px; background: #303747; border-radius: 2px; }
QSlider::handle:horizontal { background: #9287ff; width: 13px; margin: -5px 0; border-radius: 6px; }
QSlider::sub-page:horizontal { background: #7467f0; border-radius: 2px; }
QLabel#VideoCanvas { background: #080a0f; border: 1px solid #242a36; border-radius: 12px; color: #677184; }
QStatusBar { color: #8d96a8; background: #10131a; }
"""

class NovaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 780)
        self.setMinimumSize(QSize(960, 620))
        self.files = []
        self.current_index = -1
        self.user_seeking = False
        self.instance = None
        self.player = None
        if vlc:
            try:
                self.instance = vlc.Instance("--no-video-title-show", "--quiet")
                self.player = self.instance.media_player_new()
            except Exception as exc:
                self.show_vlc_error(str(exc))

        self._build_ui()
        self._build_menus()
        self.timer = QTimer(self)
        self.timer.setInterval(400)
        self.timer.timeout.connect(self.refresh_playback)
        self.timer.start()
        self.statusBar().showMessage("Prêt • Ouvrez un fichier pour commencer")

    def _build_ui(self):
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 16, 18, 14)
        root_layout.setSpacing(14)

        top = QFrame()
        top.setObjectName("Topbar")
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(18, 12, 18, 12)
        brand = QLabel("NOVA")
        brand.setObjectName("Brand")
        player_label = QLabel("PLAYER")
        player_label.setObjectName("Accent")
        brandrow = QHBoxLayout()
        brandrow.setSpacing(7)
        brandrow.addWidget(brand)
        brandrow.addWidget(player_label)
        brandwrap = QWidget()
        brandwrap.setLayout(brandrow)
        subtitle = QLabel("YOUR MEDIA. YOUR SPACE.")
        subtitle.setObjectName("Muted")
        top_layout.addWidget(brandwrap)
        top_layout.addSpacing(18)
        top_layout.addWidget(subtitle)
        top_layout.addStretch()
        self.open_button = QPushButton("+  Ajouter des médias")
        self.open_button.setObjectName("Primary")
        self.open_button.clicked.connect(self.open_files)
        top_layout.addWidget(self.open_button)
        root_layout.addWidget(top)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(225)
        sidebar.setMaximumWidth(285)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(14, 17, 14, 14)
        side.setSpacing(12)
        navtitle = QLabel("ESPACE MÉDIA")
        navtitle.setObjectName("Muted")
        side.addWidget(navtitle)
        for text in ("⌂   Accueil", "▣   Bibliothèque", "♫   Audio", "▶   Vidéos", "☆   Favoris"):
            item = QPushButton(text)
            item.setStyleSheet("text-align:left; padding:12px;")
            item.clicked.connect(lambda checked=False, t=text: self.statusBar().showMessage(t.strip()))
            side.addWidget(item)
        side.addSpacing(14)
        section = QLabel("LECTURE EN COURS")
        section.setObjectName("Muted")
        side.addWidget(section)
        self.now_playing_side = QLabel("Aucun média sélectionné")
        self.now_playing_side.setWordWrap(True)
        self.now_playing_side.setStyleSheet("font-weight:600; padding:8px;")
        side.addWidget(self.now_playing_side)
        side.addStretch()
        hint = QLabel("NOVA PLAYER  •  VERSION 1.0")
        hint.setObjectName("Muted")
        side.addWidget(hint)
        splitter.addWidget(sidebar)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(14)
        self.canvas = QLabel("NOVA PLAYER\n\nOuvrez un fichier audio ou vidéo pour commencer")
        self.canvas.setObjectName("VideoCanvas")
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setMinimumHeight(330)
        self.canvas.setStyleSheet("font-size:14pt;")
        center_layout.addWidget(self.canvas, 1)

        controls = QFrame()
        controls.setObjectName("ControlPanel")
        control_layout = QVBoxLayout(controls)
        control_layout.setContentsMargins(16, 12, 16, 12)
        control_layout.setSpacing(8)
        time_row = QHBoxLayout()
        self.position_label = QLabel("00:00")
        self.position_label.setObjectName("Muted")
        self.seek = QSlider(Qt.Horizontal)
        self.seek.setRange(0, 1000)
        self.seek.sliderPressed.connect(self._seek_pressed)
        self.seek.sliderReleased.connect(self._seek_released)
        self.duration_label = QLabel("00:00")
        self.duration_label.setObjectName("Muted")
        time_row.addWidget(self.position_label)
        time_row.addWidget(self.seek, 1)
        time_row.addWidget(self.duration_label)
        control_layout.addLayout(time_row)

        buttons = QHBoxLayout()
        buttons.addStretch()
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setObjectName("Round")
        self.prev_btn.setToolTip("Média précédent")
        self.prev_btn.clicked.connect(self.play_previous)
        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("Primary")
        self.play_btn.setMinimumWidth(58)
        self.play_btn.clicked.connect(self.toggle_play)
        self.stop_btn = QPushButton("■")
        self.stop_btn.setObjectName("Round")
        self.stop_btn.clicked.connect(self.stop)
        self.next_btn = QPushButton("⏭")
        self.next_btn.setObjectName("Round")
        self.next_btn.setToolTip("Média suivant")
        self.next_btn.clicked.connect(self.play_next)
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setObjectName("Round")
        self.fullscreen_btn.setToolTip("Plein écran")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        for btn in (self.prev_btn, self.play_btn, self.stop_btn, self.next_btn, self.fullscreen_btn):
            buttons.addWidget(btn)
        buttons.addStretch()
        self.volume_label = QLabel("VOL")
        self.volume_label.setObjectName("Muted")
        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(75)
        self.volume.setMaximumWidth(130)
        self.volume.valueChanged.connect(self.set_volume)
        buttons.addWidget(self.volume_label)
        buttons.addWidget(self.volume)
        control_layout.addLayout(buttons)
        center_layout.addWidget(controls)
        splitter.addWidget(center)

        playlist_panel = QFrame()
        playlist_panel.setObjectName("PlaylistPanel")
        playlist_panel.setMinimumWidth(235)
        playlist_panel.setMaximumWidth(330)
        playout = QVBoxLayout(playlist_panel)
        playout.setContentsMargins(14, 15, 14, 14)
        playout.setSpacing(12)
        pl_head = QHBoxLayout()
        pl_title = QLabel("Playlist")
        pl_title.setStyleSheet("font-size:14pt; font-weight:700;")
        self.count_label = QLabel("0 élément")
        self.count_label.setObjectName("Muted")
        pl_head.addWidget(pl_title)
        pl_head.addStretch()
        pl_head.addWidget(self.count_label)
        playout.addLayout(pl_head)
        self.playlist = QListWidget()
        self.playlist.itemDoubleClicked.connect(self.play_selected)
        playout.addWidget(self.playlist, 1)
        pl_buttons = QHBoxLayout()
        add = QPushButton("＋ Ajouter")
        add.clicked.connect(self.open_files)
        remove = QPushButton("− Retirer")
        remove.clicked.connect(self.remove_selected)
        clear = QPushButton("Vider")
        clear.clicked.connect(self.clear_playlist)
        pl_buttons.addWidget(add)
        pl_buttons.addWidget(remove)
        pl_buttons.addWidget(clear)
        playout.addLayout(pl_buttons)
        splitter.addWidget(playlist_panel)
        splitter.setSizes([230, 700, 270])
        root_layout.addWidget(splitter, 1)
        self.setCentralWidget(root)
        self.setStyleSheet(STYLESHEET)

    def _build_menus(self):
        file_menu = self.menuBar().addMenu("Fichier")
        open_action = QAction("Ouvrir des médias…", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_files)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        quit_action = QAction("Quitter", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        playback = self.menuBar().addMenu("Lecture")
        for label, shortcut, callback in [
            ("Lire / Pause", "Space", self.toggle_play),
            ("Arrêter", "S", self.stop),
            ("Plein écran", "F", self.toggle_fullscreen),
            ("Média suivant", "N", self.play_next),
            ("Média précédent", "P", self.play_previous),
        ]:
            action = QAction(label, self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(callback)
            playback.addAction(action)

    def open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Ajouter des médias", str(Path.home()), SUPPORTED)
        if not paths:
            return
        for path in paths:
            if path not in self.files:
                self.files.append(path)
                self.playlist.addItem(Path(path).name)
        self.count_label.setText(f"{len(self.files)} élément(s)")
        if self.current_index < 0 and self.files:
            self.play_index(len(self.files) - len(paths))

    def play_selected(self):
        row = self.playlist.currentRow()
        if 0 <= row < len(self.files):
            self.play_index(row)

    def play_index(self, index):
        if not self.files:
            return
        index %= len(self.files)
        self.current_index = index
        path = self.files[index]
        self.playlist.setCurrentRow(index)
        self.now_playing_side.setText(Path(path).name)
        self.statusBar().showMessage(f"Lecture : {Path(path).name}")
        if not self.player:
            self.show_vlc_error(VLC_IMPORT_ERROR or "Impossible d'initialiser libVLC.")
            return
        try:
            media = self.instance.media_new(path)
            self.player.set_media(media)
            self.player.audio_set_volume(self.volume.value())
            # The native VLC video surface is bound to this label on supported platforms.
            if sys.platform.startswith("win"):
                self.player.set_hwnd(int(self.canvas.winId()))
            elif sys.platform == "darwin":
                self.player.set_nsobject(int(self.canvas.winId()))
            else:
                self.player.set_xwindow(int(self.canvas.winId()))
            self.player.play()
            self.play_btn.setText("Ⅱ")
            self.canvas.setText("")
        except Exception as exc:
            self.show_vlc_error(str(exc))

    def toggle_play(self):
        if not self.player:
            self.show_vlc_error(VLC_IMPORT_ERROR or "libVLC n'est pas disponible.")
            return
        try:
            if self.player.is_playing():
                self.player.pause()
                self.play_btn.setText("▶")
            elif self.current_index >= 0:
                self.player.play()
                self.play_btn.setText("Ⅱ")
            elif self.files:
                self.play_index(0)
            else:
                self.open_files()
        except Exception as exc:
            self.show_vlc_error(str(exc))

    def stop(self):
        if self.player:
            self.player.stop()
        self.play_btn.setText("▶")
        self.seek.setValue(0)
        self.position_label.setText("00:00")

    def play_next(self):
        if self.files:
            self.play_index((self.current_index + 1) % len(self.files))

    def play_previous(self):
        if self.files:
            self.play_index((self.current_index - 1) % len(self.files))

    def set_volume(self, value):
        if self.player:
            self.player.audio_set_volume(value)

    def _seek_pressed(self):
        self.user_seeking = True

    def _seek_released(self):
        self.user_seeking = False
        if self.player:
            length = self.player.get_length()
            if length > 0:
                self.player.set_time(int(length * self.seek.value() / 1000))

    def refresh_playback(self):
        if not self.player:
            return
        try:
            length = self.player.get_length()
            current = self.player.get_time()
            if length > 0:
                if not self.user_seeking:
                    self.seek.setValue(int(current / length * 1000))
                self.duration_label.setText(self.format_time(length))
                self.position_label.setText(self.format_time(max(0, current)))
            if self.player.get_state() == vlc.State.Ended and self.current_index >= 0:
                self.play_next()
        except Exception:
            pass

    @staticmethod
    def format_time(milliseconds):
        seconds = max(0, milliseconds // 1000)
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def remove_selected(self):
        row = self.playlist.currentRow()
        if row < 0:
            return
        if row == self.current_index and self.player:
            self.player.stop()
        self.files.pop(row)
        self.playlist.takeItem(row)
        if self.current_index == row:
            self.current_index = -1
            self.now_playing_side.setText("Aucun média sélectionné")
        elif row < self.current_index:
            self.current_index -= 1
        self.count_label.setText(f"{len(self.files)} élément(s)")

    def clear_playlist(self):
        if self.player:
            self.player.stop()
        self.files.clear()
        self.playlist.clear()
        self.current_index = -1
        self.count_label.setText("0 élément")
        self.now_playing_side.setText("Aucun média sélectionné")
        self.canvas.setText("NOVA PLAYER\n\nOuvrez un fichier audio ou vidéo pour commencer")
        self.play_btn.setText("▶")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_vlc_error(self, details):
        QMessageBox.warning(
            self, "Moteur multimédia indisponible",
            "NOVA Player n'a pas pu initialiser VLC/libVLC.\n\n"
            "Installez VLC Media Player et vérifiez que libVLC est accessible.\n\n"
            f"Détail : {details}"
        )

    def closeEvent(self, event):
        try:
            if self.player:
                self.player.stop()
        except Exception:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = NovaPlayer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
