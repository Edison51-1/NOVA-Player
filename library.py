"""Bibliothèque persistante (JSON) + analyse des durées / miniatures."""
import hashlib
import json
from pathlib import Path

from PySide6.QtCore import QObject, QStandardPaths, QTimer, QUrl, Signal
from PySide6.QtGui import QImage
from PySide6.QtMultimedia import QMediaPlayer, QVideoSink
from PySide6.QtCore import Qt

VIDEO_EXT = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv", ".m4v", ".mpg", ".mpeg", ".ts", ".3gp"}
AUDIO_EXT = {".mp3", ".wav", ".flac", ".ogg", ".oga", ".m4a", ".aac", ".wma", ".opus"}
ALL_EXT = VIDEO_EXT | AUDIO_EXT


def data_dir() -> Path:
    base = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation) or str(Path.home() / ".nova-player")
    p = Path(base)
    (p / "thumbs").mkdir(parents=True, exist_ok=True)
    return p


def kind_of(path: str) -> str:
    return "audio" if Path(path).suffix.lower() in AUDIO_EXT else "video"


def fmt_time(ms: int) -> str:
    s = max(0, int(ms // 1000))
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


class Library:
    def __init__(self):
        self.file = data_dir() / "library.json"
        self.items: list[dict] = []
        self.load()

    def load(self):
        try:
            self.items = [i for i in json.loads(self.file.read_text("utf-8")) if Path(i["path"]).exists()]
        except Exception:
            self.items = []

    def save(self):
        try:
            self.file.write_text(json.dumps(self.items, ensure_ascii=False, indent=1), "utf-8")
        except Exception:
            pass

    def find(self, path: str):
        return next((i for i in self.items if i["path"] == path), None)

    def add(self, paths) -> list[str]:
        """Ajoute des fichiers/dossiers ; renvoie les chemins réellement ajoutés."""
        added = []
        for raw in paths:
            p = Path(raw)
            files = sorted(q for q in p.rglob("*") if q.is_file()) if p.is_dir() else [p]
            for f in files:
                if f.suffix.lower() not in ALL_EXT or self.find(str(f)):
                    continue
                self.items.append({"path": str(f), "title": f.stem, "duration": 0,
                                   "favorite": False, "kind": kind_of(str(f)), "thumb": ""})
                added.append(str(f))
        if added:
            self.save()
        return added

    def remove(self, paths):
        self.items = [i for i in self.items if i["path"] not in set(paths)]
        self.save()

    def clear(self):
        self.items = []
        self.save()


class MetaProbe(QObject):
    """Lit en arrière-plan la durée et une image (miniature) de chaque média."""
    done = Signal(str)

    def __init__(self, library: Library):
        super().__init__()
        self.lib = library
        self.queue: list[str] = []
        self.current = None
        self.image = None
        self.target = 0
        self.seeking = False
        self.player = QMediaPlayer()
        self.sink = QVideoSink()
        self.player.setVideoSink(self.sink)
        self.player.mediaStatusChanged.connect(self._status)
        self.sink.videoFrameChanged.connect(self._frame)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(4000)
        self.timer.timeout.connect(self._finish)

    def enqueue(self, path: str):
        it = self.lib.find(path)
        if not it or path in self.queue or path == self.current:
            return
        thumb_ok = it["kind"] == "audio" or (it["thumb"] and Path(it["thumb"]).exists())
        if it["duration"] and thumb_ok:
            return
        self.queue.append(path)
        if self.current is None:
            self._next()

    def _next(self):
        if not self.queue:
            self.current = None
            return
        self.current = self.queue.pop(0)
        self.image, self.seeking, self.target = None, False, 0
        self.timer.start()
        self.player.setSource(QUrl.fromLocalFile(self.current))

    def _status(self, status):
        if self.current is None:
            return
        S = QMediaPlayer.MediaStatus
        if status == S.InvalidMedia:
            self._finish()
        elif status == S.LoadedMedia and not self.seeking:
            dur = self.player.duration()
            it = self.lib.find(self.current)
            if it and dur > 0:
                it["duration"] = dur
            if it and it["kind"] == "video" and self.player.hasVideo():
                self.seeking = True
                self.target = max(500, dur // 8)
                self.player.setPosition(self.target)
                self.player.play()
            else:
                self._finish()

    def _frame(self, frame):
        if not self.seeking or not frame.isValid():
            return
        img = frame.toImage()
        if img.isNull():
            return
        self.image = img
        if frame.startTime() >= (self.target - 200) * 1000:
            self._finish()

    def _finish(self):
        self.timer.stop()
        path, self.current, self.seeking = self.current, None, False
        self.player.stop()
        self.player.setSource(QUrl())
        if path:
            it = self.lib.find(path)
            if it and self.image is not None:
                out = data_dir() / "thumbs" / (hashlib.md5(path.encode()).hexdigest() + ".png")
                small = self.image.scaled(240, 150, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                if small.save(str(out)):
                    it["thumb"] = str(out)
            self.lib.save()
            self.done.emit(path)
        self.image = None
        self._next()
