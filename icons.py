"""Icônes vectorielles (SVG) dessinées à la volée : aucune image externe nécessaire."""
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

PATHS = {
    "play": '<path d="M8 5v14l11-7z"/>',
    "pause": '<path d="M6 5h4v14H6zM14 5h4v14h-4z"/>',
    "stop": '<rect x="6" y="6" width="12" height="12" rx="1.5"/>',
    "prev": '<path d="M6 6h2v12H6zM9.5 12 18 18V6z"/>',
    "next": '<path d="M16 6h2v12h-2zM6 18l8.5-6L6 6z"/>',
    "fullscreen": '<path d="M4 4h6v2H6v4H4zM14 4h6v6h-2V6h-4zM4 14h2v4h4v2H4zM18 14h2v6h-6v-2h4z"/>',
    "volume": '<path d="M3 9v6h4l5 4V5L7 9z"/><path d="M15.5 8.5a5 5 0 0 1 0 7l-1.4-1.4a3 3 0 0 0 0-4.2z"/><path d="M18.4 5.6a9 9 0 0 1 0 12.8l-1.4-1.4a7 7 0 0 0 0-10z"/>',
    "mute": '<path d="M3 9v6h4l5 4V5L7 9z"/><path d="M15 9.4 16.4 8l1.6 1.6L19.6 8 21 9.4 19.4 11 21 12.6 19.6 14 18 12.4 16.4 14 15 12.6 16.6 11z"/>',
    "home": '<path d="M12 3 2 12h3v8h5v-5h4v5h5v-8h3z"/>',
    "folder": '<path d="M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "music": '<path d="M12 3v10.55A4 4 0 1 0 14 17V7h4V3z"/>',
    "star": '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21 7 14.2l-5-4.9 6.9-1z"/>',
    "plus": '<path d="M11 4h2v7h7v2h-7v7h-2v-7H4v-2h7z"/>',
    "minus": '<path d="M4 11h16v2H4z"/>',
    "trash": '<path d="M9 3h6l1 2h4v2H4V5h4zM6 9h12l-1 12H7z"/>',
    "film": '<path d="M4 4h16a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1zm2 2v2h2V6zm10 0v2h2V6zM6 11v2h2v-2zm10 0v2h2v-2zM6 16v2h2v-2zm10 0v2h2v-2z"/>',
}

LOGO = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><defs>'
    '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#c9b8ff"/><stop offset="1" stop-color="#6d4aff"/>'
    '</linearGradient></defs>'
    '<path fill="url(#g)" d="M5 2.5 22 12 5 21.5l3.4-9.5z"/></svg>'
)


def _render(svg: str, size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(QByteArray(svg.encode())).render(p)
    p.end()
    return pm


def pixmap(name: str, color: str = "#ffffff", size: int = 64) -> QPixmap:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           f'fill="{color}">{PATHS[name]}</svg>')
    return _render(svg, size)


def icon(name: str, color: str = "#ffffff") -> QIcon:
    return QIcon(pixmap(name, color, 64))


def logo_pixmap(size: int = 256) -> QPixmap:
    return _render(LOGO, size)


def logo_icon() -> QIcon:
    ic = QIcon()
    for s in (16, 32, 48, 64, 128, 256):
        ic.addPixmap(logo_pixmap(s))
    return ic
