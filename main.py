"""NOVA Player — lecteur audio & vidéo (PySide6). YOUR MEDIA. YOUR SPACE."""
import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QUrl, Signal
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFileDialog, QFrame, QHBoxLayout, QLabel,
                               QListWidget, QListWidgetItem, QMainWindow, QMenu, QMessageBox,
                               QPushButton, QSlider, QStackedLayout, QStyle, QVBoxLayout, QWidget)

import icons
from library import ALL_EXT, AUDIO_EXT, VIDEO_EXT, Library, MetaProbe, fmt_time
from style import QSS

VERSION = "1.0"
_LOG = None


def log(msg):
    """Ajoute une ligne au journal ~/NOVA-Player-log.txt (si disponible)."""
    if _LOG:
        try:
            _LOG.write(msg + "\n")
        except Exception:
            pass


def mk_btn(name, obj, size, icon_size, tip="", color="#ffffff"):
    b = QPushButton()
    b.setObjectName(obj)
    b.setIcon(icons.icon(name, color))
    b.setIconSize(QSize(icon_size, icon_size))
    b.setFixedSize(size, size)
    b.setCursor(Qt.PointingHandCursor)
    b.setToolTip(tip)
    return b


class _NullAudio:
    """Remplace QAudioOutput quand aucun périphérique audio n'existe (tests / CI)."""
    _muted = False
    def setVolume(self, _v): pass
    def setMuted(self, m): self._muted = m
    def isMuted(self): return self._muted


class JumpSlider(QSlider):
    """Slider qui saute directement à l'endroit cliqué."""
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.maximum() > 0:
            v = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), int(e.position().x()), self.width())
            self.setValue(v)
            self.sliderMoved.emit(v)
        super().mousePressEvent(e)


class VideoWidget(QVideoWidget):
    doubleClicked = Signal()

    def mouseDoubleClickEvent(self, e):
        self.doubleClicked.emit()


class ItemWidget(QWidget):
    def __init__(self, item: dict):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(14)
        thumb = QLabel()
        thumb.setFixedSize(84, 52)
        pm = QPixmap(item["thumb"]) if item.get("thumb") else QPixmap()
        if pm.isNull():
            pm = icons.pixmap("music" if item["kind"] == "audio" else "film", "#8e6dff", 40)
            thumb.setAlignment(Qt.AlignCenter)
            thumb.setStyleSheet("background:#1b1740;border-radius:6px;")
        else:
            pm = pm.scaled(84, 52, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            thumb.setStyleSheet("border-radius:6px;")
        thumb.setPixmap(pm)
        col = QVBoxLayout()
        col.setSpacing(2)
        star = "★ " if item.get("favorite") else ""
        title = QLabel(star + item["title"])
        title.setStyleSheet("font-size:15px;color:#fff;")
        dur = QLabel(fmt_time(item["duration"]) if item["duration"] else "--:--:--")
        dur.setStyleSheet("color:#b9b5d8;")
        col.addStretch()
        col.addWidget(title)
        col.addWidget(dur)
        col.addStretch()
        lay.addWidget(thumb)
        lay.addLayout(col, 1)


class MainWindow(QMainWindow):
    NAV = [("Accueil", "home", "all"), ("Audio", "music", "audio"),
           ("Vidéos", "play", "video"), ("Favoris", "star", "fav")]
    TITLES = {"all": "Playlist", "audio": "Audio", "video": "Vidéos", "fav": "Favoris"}

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NOVA Player")
        self.setWindowIcon(icons.logo_icon())
        self.resize(1320, 780)
        self.setMinimumSize(1020, 640)
        self.setAcceptDrops(True)
        self.lib = Library()
        self.probe = MetaProbe(self.lib)
        self.probe.done.connect(lambda _p: self.refresh_list())
        self.mode = "all"
        self.current = None
        self.view_paths: list[str] = []
        self._dark_done = False

        self.player = QMediaPlayer()
        self.audio = QAudioOutput() if not os.environ.get("NOVA_NO_AUDIO") else _NullAudio()
        if not isinstance(self.audio, _NullAudio):
            self.player.setAudioOutput(self.audio)
        self.audio.setVolume(0.75)

        self._build_ui()
        self._wire()
        self.refresh_list()
        for it in self.lib.items:
            self.probe.enqueue(it["path"])

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        root = QWidget(objectName="root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # En-tête
        self.header = QFrame(objectName="header")
        self.header.setFixedHeight(120)
        h = QHBoxLayout(self.header)
        h.setContentsMargins(36, 0, 36, 0)
        logo = QLabel()
        logo.setPixmap(icons.logo_pixmap(56))
        nova = QLabel("NOVA", objectName="brandNova")
        player = QLabel("PLAYER", objectName="brandPlayer")
        sep = QFrame(objectName="vsep")
        sep.setFixedSize(2, 36)
        tag = QLabel("YOUR MEDIA. YOUR SPACE.", objectName="tagline")
        self.btn_add_media = QPushButton("  Ajouter des médias", objectName="addMedia")
        self.btn_add_media.setIcon(icons.icon("plus"))
        self.btn_add_media.setIconSize(QSize(20, 20))
        self.btn_add_media.setCursor(Qt.PointingHandCursor)
        h.addWidget(logo)
        h.addSpacing(26)
        h.addWidget(nova)
        h.addSpacing(8)
        h.addWidget(player)
        h.addSpacing(22)
        h.addWidget(sep)
        h.addSpacing(22)
        h.addWidget(tag)
        h.addStretch()
        h.addWidget(self.btn_add_media)
        outer.addWidget(self.header)

        body = QHBoxLayout()
        body.setContentsMargins(14, 14, 14, 14)
        body.setSpacing(14)
        outer.addLayout(body, 1)

        # Barre latérale
        self.sidebar = QFrame(objectName="sidebar")
        self.sidebar.setFixedWidth(290)
        s = QVBoxLayout(self.sidebar)
        s.setContentsMargins(18, 22, 18, 16)
        s.setSpacing(6)
        s.addWidget(QLabel("ESPACE MÉDIA", objectName="sectionTitle"))
        s.addSpacing(8)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_btns = {}
        for i, (label, ic, mode) in enumerate(self.NAV):
            b = QPushButton("  " + label, objectName="navBtn")
            b.setCheckable(True)
            b.setIcon(icons.icon(ic))
            b.setIconSize(QSize(24, 24))
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, m=mode: self.set_mode(m))
            self.nav_group.addButton(b)
            self.nav_btns[mode] = b
            s.addWidget(b)
            if i == 0:
                self.btn_library = QPushButton("  Bibliothèque", objectName="navBtn")
                self.btn_library.setIcon(icons.icon("folder"))
                self.btn_library.setIconSize(QSize(24, 24))
                self.btn_library.setCursor(Qt.PointingHandCursor)
                self.btn_library.setToolTip("Importer un dossier entier")
                s.addWidget(self.btn_library)
        self.nav_btns["all"].setChecked(True)
        s.addSpacing(10)
        s.addWidget(QFrame(objectName="hline", fixedHeight=1))
        s.addSpacing(14)
        s.addWidget(QLabel("LECTURE EN COURS", objectName="sectionTitle"))
        s.addSpacing(6)
        now = QHBoxLayout()
        now.setSpacing(12)
        self.now_thumb = QLabel()
        self.now_thumb.setFixedSize(96, 62)
        self.now_thumb.setAlignment(Qt.AlignCenter)
        self.now_thumb.setStyleSheet("background:#1b1740;border-radius:6px;")
        nc = QVBoxLayout()
        self.now_title = QLabel("Aucun média", objectName="nowTitle")
        self.now_title.setWordWrap(True)
        self.now_time = QLabel("00:00:00 / 00:00:00", objectName="nowTime")
        nc.addStretch()
        nc.addWidget(self.now_title)
        nc.addWidget(self.now_time)
        nc.addStretch()
        now.addWidget(self.now_thumb)
        now.addLayout(nc, 1)
        s.addLayout(now)
        s.addStretch()
        s.addWidget(QLabel(f"NOVA PLAYER  •  VERSION {VERSION}", objectName="version", alignment=Qt.AlignCenter))
        body.addWidget(self.sidebar)

        # Centre
        center = QFrame(objectName="centerPanel")
        c = QVBoxLayout(center)
        c.setContentsMargins(18, 18, 18, 14)
        c.setSpacing(10)
        host = QFrame(objectName="videoHost")
        self.stack = QStackedLayout(host)
        self.stack.setContentsMargins(0, 0, 0, 0)
        self.video = VideoWidget()
        self.player.setVideoOutput(self.video)
        self.audio_page = QFrame(objectName="audioPage")
        ap = QVBoxLayout(self.audio_page)
        ap.setAlignment(Qt.AlignCenter)
        self.audio_icon = QLabel(alignment=Qt.AlignCenter)
        self.audio_icon.setPixmap(icons.pixmap("music", "#8e6dff", 120))
        self.audio_title = QLabel("NOVA Player", objectName="audioTitle", alignment=Qt.AlignCenter)
        self.audio_hint = QLabel("Ajoutez des médias ou glissez-déposez vos fichiers ici",
                                 objectName="audioHint", alignment=Qt.AlignCenter)
        ap.addWidget(self.audio_icon)
        ap.addWidget(self.audio_title)
        ap.addWidget(self.audio_hint)
        self.stack.addWidget(self.video)
        self.stack.addWidget(self.audio_page)
        self.stack.setCurrentIndex(1)
        c.addWidget(host, 1)

        seek = QHBoxLayout()
        self.lbl_pos = QLabel("00:00:00", objectName="timeLabel")
        self.lbl_dur = QLabel("00:00:00", objectName="timeLabel")
        self.seek = JumpSlider(Qt.Horizontal)
        self.seek.setCursor(Qt.PointingHandCursor)
        seek.addWidget(self.lbl_pos)
        seek.addSpacing(10)
        seek.addWidget(self.seek, 1)
        seek.addSpacing(10)
        seek.addWidget(self.lbl_dur)
        c.addLayout(seek)

        ctr = QHBoxLayout()
        ctr.setSpacing(18)
        ctr.addStretch()
        self.b_prev = mk_btn("prev", "ctrl", 56, 24, "Précédent (P)")
        self.b_play = mk_btn("play", "ctrlMain", 70, 32, "Lecture / Pause (Espace)")
        self.b_stop = mk_btn("stop", "ctrl", 56, 22, "Arrêter")
        self.b_next = mk_btn("next", "ctrl", 56, 24, "Suivant (N)")
        self.b_full = mk_btn("fullscreen", "ctrl", 56, 22, "Plein écran (F)")
        for b in (self.b_prev, self.b_play, self.b_stop, self.b_next, self.b_full):
            ctr.addWidget(b)
        ctr.addStretch()
        c.addLayout(ctr)

        vol = QHBoxLayout()
        self.b_mute = mk_btn("volume", "iconBtn", 36, 24, "Muet (M)", "#d6d3ee")
        self.vol = JumpSlider(Qt.Horizontal)
        self.vol.setRange(0, 100)
        self.vol.setValue(75)
        self.vol.setFixedWidth(240)
        self.lbl_vol = QLabel("75%", objectName="volLabel")
        vol.addSpacing(6)
        vol.addWidget(self.b_mute)
        vol.addWidget(QLabel("VOL", objectName="volLabel"))
        vol.addSpacing(6)
        vol.addWidget(self.vol)
        vol.addSpacing(10)
        vol.addWidget(self.lbl_vol)
        vol.addStretch()
        c.addLayout(vol)
        body.addWidget(center, 1)

        # Playlist
        self.panel = QFrame(objectName="playlistPanel")
        self.panel.setFixedWidth(380)
        p = QVBoxLayout(self.panel)
        p.setContentsMargins(18, 20, 18, 18)
        top = QHBoxLayout()
        self.pl_title = QLabel("Playlist", objectName="playlistTitle")
        self.pl_count = QLabel("0 élément(s)", objectName="countLabel")
        top.addWidget(self.pl_title)
        top.addStretch()
        top.addWidget(self.pl_count)
        p.addLayout(top)
        self.listw = QListWidget()
        self.listw.setIconSize(QSize(1, 1))
        self.listw.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.listw.setContextMenuPolicy(Qt.CustomContextMenu)
        p.addWidget(self.listw, 1)
        bt = QHBoxLayout()
        self.pb_add = QPushButton("  Ajouter", objectName="plBtn")
        self.pb_add.setIcon(icons.icon("plus"))
        self.pb_rem = QPushButton("  Retirer", objectName="plBtn")
        self.pb_rem.setIcon(icons.icon("minus"))
        self.pb_clr = QPushButton("  Vider", objectName="plBtn")
        self.pb_clr.setIcon(icons.icon("trash"))
        for b in (self.pb_add, self.pb_rem, self.pb_clr):
            b.setCursor(Qt.PointingHandCursor)
            bt.addWidget(b)
        p.addLayout(bt)
        body.addWidget(self.panel)

    def _wire(self):
        self.btn_add_media.clicked.connect(self.add_files)
        self.pb_add.clicked.connect(self.add_files)
        self.btn_library.clicked.connect(self.add_folder)
        self.pb_rem.clicked.connect(self.remove_selected)
        self.pb_clr.clicked.connect(self.clear_all)
        self.listw.itemDoubleClicked.connect(lambda it: self.play_path(it.data(Qt.UserRole)))
        self.listw.customContextMenuRequested.connect(self.context_menu)

        self.b_play.clicked.connect(self.toggle_play)
        self.b_stop.clicked.connect(self.stop)
        self.b_next.clicked.connect(self.next)
        self.b_prev.clicked.connect(self.prev)
        self.b_full.clicked.connect(self.toggle_fullscreen)
        self.video.doubleClicked.connect(self.toggle_fullscreen)
        self.b_mute.clicked.connect(self.toggle_mute)

        self.seek.sliderMoved.connect(self.player.setPosition)
        self.vol.valueChanged.connect(self.set_volume)
        self.player.positionChanged.connect(self.on_position)
        self.player.durationChanged.connect(self.on_duration)
        self.player.playbackStateChanged.connect(self.on_state)
        self.player.mediaStatusChanged.connect(self.on_status)
        self.player.errorOccurred.connect(self.on_error)

        for keys, fn in [("Space", self.toggle_play), ("F", self.toggle_fullscreen), ("F11", self.toggle_fullscreen),
                         ("Esc", self.exit_fullscreen), ("M", self.toggle_mute), ("N", self.next), ("P", self.prev),
                         ("Right", lambda: self.skip(5000)), ("Left", lambda: self.skip(-5000)),
                         ("Up", lambda: self.vol.setValue(self.vol.value() + 5)),
                         ("Down", lambda: self.vol.setValue(self.vol.value() - 5)),
                         ("Ctrl+O", self.add_files)]:
            sc = QShortcut(QKeySequence(keys), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(fn)

    # -------------------------------------------------------------- library
    def filtered(self):
        items = self.lib.items
        if self.mode == "audio":
            return [i for i in items if i["kind"] == "audio"]
        if self.mode == "video":
            return [i for i in items if i["kind"] == "video"]
        if self.mode == "fav":
            return [i for i in items if i["favorite"]]
        return list(items)

    def set_mode(self, mode):
        self.mode = mode
        self.refresh_list()

    def refresh_list(self):
        items = self.filtered()
        self.view_paths = [i["path"] for i in items]
        self.listw.blockSignals(True)
        self.listw.clear()
        for it in items:
            li = QListWidgetItem()
            li.setData(Qt.UserRole, it["path"])
            li.setSizeHint(QSize(0, 70))
            self.listw.addItem(li)
            self.listw.setItemWidget(li, ItemWidget(it))
            if it["path"] == self.current:
                self.listw.setCurrentItem(li)
        self.listw.blockSignals(False)
        self.pl_title.setText(self.TITLES[self.mode])
        self.pl_count.setText(f"{len(items)} élément(s)")
        self.update_now_playing()

    def add_files(self):
        exts = " ".join("*" + e for e in sorted(ALL_EXT))
        files, _ = QFileDialog.getOpenFileNames(self, "Ajouter des médias", str(Path.home()),
                                                f"Médias ({exts});;Tous les fichiers (*)")
        self.import_paths(files)

    def add_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Importer un dossier", str(Path.home()))
        if d:
            self.import_paths([d])

    def import_paths(self, paths, autoplay=False):
        added = self.lib.add(paths)
        self.refresh_list()
        for p in added:
            self.probe.enqueue(p)
        if added and (autoplay or self.current is None):
            self.play_path(added[0])

    def remove_selected(self):
        sel = [i.data(Qt.UserRole) for i in self.listw.selectedItems()]
        if not sel:
            return
        if self.current in sel:
            self.stop()
            self.current = None
        self.lib.remove(sel)
        self.refresh_list()

    def clear_all(self):
        if not self.lib.items:
            return
        r = QMessageBox.question(self, "Vider la playlist", "Retirer tous les éléments de la liste ?\n(Vos fichiers ne sont pas supprimés.)")
        if r == QMessageBox.Yes:
            self.stop()
            self.current = None
            self.lib.clear()
            self.refresh_list()

    def context_menu(self, pos):
        li = self.listw.itemAt(pos)
        if not li:
            return
        path = li.data(Qt.UserRole)
        it = self.lib.find(path)
        m = QMenu(self)
        a_play = m.addAction("Lire")
        a_fav = m.addAction("Retirer des favoris" if it["favorite"] else "Ajouter aux favoris")
        a_rem = m.addAction("Retirer de la liste")
        act = m.exec(self.listw.mapToGlobal(pos))
        if act == a_play:
            self.play_path(path)
        elif act == a_fav:
            it["favorite"] = not it["favorite"]
            self.lib.save()
            self.refresh_list()
        elif act == a_rem:
            self.listw.setCurrentItem(li)
            self.remove_selected()

    # -------------------------------------------------------------- playback
    def play_path(self, path):
        it = self.lib.find(path)
        if not it:
            return
        self.current = path
        self.player.setSource(QUrl.fromLocalFile(path))
        self.stack.setCurrentIndex(0 if it["kind"] == "video" else 1)
        self.audio_title.setText(it["title"])
        self.audio_hint.setText("Lecture audio")
        self.player.play()
        for i in range(self.listw.count()):
            if self.listw.item(i).data(Qt.UserRole) == path:
                self.listw.setCurrentRow(i)
        self.update_now_playing()

    def toggle_play(self):
        S = QMediaPlayer.PlaybackState
        if self.player.playbackState() == S.PlayingState:
            self.player.pause()
        elif self.current and self.player.source().isValid():
            self.player.play()
        else:
            sel = self.listw.currentItem()
            path = sel.data(Qt.UserRole) if sel else (self.view_paths[0] if self.view_paths else None)
            if path:
                self.play_path(path)
            else:
                self.add_files()

    def stop(self):
        self.player.stop()
        self.seek.setValue(0)

    def _neighbor(self, step):
        if not self.view_paths:
            return None
        if self.current in self.view_paths:
            return self.view_paths[(self.view_paths.index(self.current) + step) % len(self.view_paths)]
        return self.view_paths[0]

    def next(self):
        p = self._neighbor(1)
        if p:
            self.play_path(p)

    def prev(self):
        if self.player.position() > 3000 and self.current:
            self.player.setPosition(0)
            return
        p = self._neighbor(-1)
        if p:
            self.play_path(p)

    def skip(self, ms):
        if self.current:
            self.player.setPosition(max(0, min(self.player.duration(), self.player.position() + ms)))

    def set_volume(self, v):
        v = max(0, min(100, v))
        if v != self.vol.value():
            self.vol.setValue(v)
            return
        self.audio.setVolume(v / 100)
        self.audio.setMuted(False)
        self.lbl_vol.setText(f"{v}%")
        self.b_mute.setIcon(icons.icon("mute" if v == 0 else "volume", "#d6d3ee"))

    def toggle_mute(self):
        m = not self.audio.isMuted()
        self.audio.setMuted(m)
        self.b_mute.setIcon(icons.icon("mute" if m else "volume", "#d6d3ee"))

    # -------------------------------------------------------------- events
    def on_position(self, pos):
        if not self.seek.isSliderDown():
            self.seek.setValue(pos)
        self.lbl_pos.setText(fmt_time(pos))
        self.now_time.setText(f"{fmt_time(pos)} / {fmt_time(self.player.duration())}")

    def on_duration(self, dur):
        self.seek.setRange(0, max(0, dur))
        self.lbl_dur.setText(fmt_time(dur))
        it = self.lib.find(self.current) if self.current else None
        if it and dur > 0 and it["duration"] != dur:
            it["duration"] = dur
            self.lib.save()

    def on_state(self, state):
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self.b_play.setIcon(icons.icon("pause" if playing else "play"))

    def on_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.current in self.view_paths and self.view_paths.index(self.current) < len(self.view_paths) - 1:
                self.next()
            else:
                self.stop()

    def on_error(self, err, msg):
        log(f"Erreur média : {err} | {msg} | fichier : {self.current} | "
            f"backend : {os.environ.get('QT_MEDIA_BACKEND', 'par défaut')}")
        self.stack.setCurrentIndex(1)
        self.audio_title.setText("Lecture impossible")
        self.audio_hint.setText(msg or "Format non pris en charge")

    def update_now_playing(self):
        it = self.lib.find(self.current) if self.current else None
        if not it:
            self.now_title.setText("Aucun média")
            self.now_thumb.setPixmap(icons.pixmap("film", "#8e6dff", 36))
            return
        self.now_title.setText(it["title"])
        pm = QPixmap(it["thumb"]) if it.get("thumb") else QPixmap()
        if pm.isNull():
            pm = icons.pixmap("music" if it["kind"] == "audio" else "film", "#8e6dff", 36)
        else:
            pm = pm.scaled(96, 62, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.now_thumb.setPixmap(pm)

    # -------------------------------------------------------------- window
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.exit_fullscreen()
        else:
            for w in (self.header, self.sidebar, self.panel):
                w.hide()
            self.showFullScreen()

    def exit_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            for w in (self.header, self.sidebar, self.panel):
                w.show()

    def showEvent(self, e):
        super().showEvent(e)
        if not self._dark_done and sys.platform == "win32":
            self._dark_done = True
            try:  # barre de titre sombre sous Windows 10/11
                import ctypes
                v = ctypes.c_int(1)
                hwnd = int(self.winId())
                for attr in (20, 19):
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(v), ctypes.sizeof(v))
            except Exception:
                pass

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        self.import_paths([u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()], autoplay=True)

    def closeEvent(self, e):
        self.player.stop()
        self.lib.save()
        super().closeEvent(e)


def _setup_crash_log():
    """Écrit les erreurs dans ~/NOVA-Player-log.txt (utile quand l'appli est lancée sans console)."""
    import faulthandler
    import traceback
    global _LOG
    log_path = Path.home() / "NOVA-Player-log.txt"
    try:
        f = open(log_path, "a", encoding="utf-8", buffering=1)
        _LOG = f
        f.write(f"\n--- Démarrage NOVA Player {VERSION} | Python {sys.version.split()[0]} | {sys.platform} ---\n")
        faulthandler.enable(file=f, all_threads=True)
    except Exception:
        return log_path

    def hook(etype, value, tb):
        text = "".join(traceback.format_exception(etype, value, tb))
        try:
            f.write(text)
            QMessageBox.critical(None, "NOVA Player - erreur", f"{text[-1200:]}\n\nJournal : {log_path}")
        except Exception:
            pass
    sys.excepthook = hook
    return log_path


def main():
    _setup_crash_log()
    app = QApplication(sys.argv)
    app.setApplicationName("NOVA Player")
    app.setOrganizationName("NovaPlayer")
    app.setStyleSheet(QSS)
    win = MainWindow()
    log(f"Fenêtre créée | backend : {os.environ.get('QT_MEDIA_BACKEND', 'par défaut')}")
    win.show()
    win.raise_()
    win.activateWindow()
    args = [a for a in sys.argv[1:] if Path(a).exists()]
    if args:  # « Ouvrir avec NOVA Player »
        win.import_paths(args, autoplay=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
