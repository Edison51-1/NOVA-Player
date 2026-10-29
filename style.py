"""Feuille de style (QSS) du thème sombre violet de NOVA Player."""

ACCENT = "#7c5cff"
ACCENT_DARK = "#4b3a9e"

QSS = f"""
* {{ font-family: "Segoe UI", "Inter", "Noto Sans", sans-serif; font-size: 14px; color: #e9e7f7; }}
QMainWindow, #root {{ background: #0c0a18; }}
QToolTip {{ background: #1b1735; color: #fff; border: 1px solid #3a3070; padding: 4px 8px; }}

#header {{ background: #0e0c1d; border-bottom: 1px solid #1c1836; }}
#brandNova {{ font-size: 40px; font-weight: 800; font-style: italic; color: #ffffff; }}
#brandPlayer {{ font-size: 40px; font-weight: 300; font-style: italic; color: #8e6dff; }}
#tagline {{ font-size: 18px; font-style: italic; color: #8b87ad; letter-spacing: 1px; }}
#vsep {{ background: #2a2548; }}

#sidebar, #playlistPanel {{ background: #12102a; border: 1px solid #1c1836; border-radius: 16px; }}
#centerPanel {{ background: #0f0d20; border: 1px solid #1c1836; border-radius: 16px; }}
#sectionTitle {{ font-size: 15px; font-weight: 700; color: #9a95c4; letter-spacing: 0.5px; }}
#playlistTitle {{ font-size: 22px; font-weight: 700; color: #fff; }}
#countLabel {{ color: #b9b5d8; }}
#hline {{ background: #1f1b3d; }}

QPushButton {{ background: transparent; border: none; }}
#navBtn {{ text-align: left; padding: 11px 14px; border-radius: 10px; font-size: 15px; color: #d6d3ee; }}
#navBtn:hover {{ background: #1b1740; }}
#navBtn:checked {{ background: {ACCENT_DARK}; color: #fff; }}

#addMedia {{ background: {ACCENT}; color: #fff; border-radius: 14px; padding: 14px 26px; font-size: 16px; font-weight: 600; }}
#addMedia:hover {{ background: #8c70ff; }}
#addMedia:pressed {{ background: #6a4bf0; }}

#ctrl {{ background: #1a1736; border: 1px solid #2c2754; border-radius: 28px; }}
#ctrl:hover {{ background: #25204a; }}
#ctrlMain {{ background: {ACCENT}; border-radius: 35px; }}
#ctrlMain:hover {{ background: #8c70ff; }}
#plBtn {{ background: #1a1736; border: 1px solid #2c2754; border-radius: 10px; padding: 9px 14px; }}
#plBtn:hover {{ background: #25204a; }}
#iconBtn {{ border-radius: 8px; padding: 4px; }}
#iconBtn:hover {{ background: #1f1b44; }}

#timeLabel {{ font-size: 15px; color: #dcd9f2; }}
#volLabel {{ font-size: 13px; color: #cfcbeb; letter-spacing: 1px; }}
#nowTitle {{ font-weight: 700; color: #fff; }}
#nowTime {{ font-size: 13px; color: #c9c5e6; }}
#version {{ font-size: 11px; color: #8b87ad; letter-spacing: 1px; }}

#videoHost {{ background: #05040c; border-radius: 12px; }}
#audioPage {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1d1647, stop:1 #0a0818); border-radius: 12px; }}
#audioTitle {{ font-size: 26px; font-weight: 700; color: #fff; }}
#audioHint {{ color: #9a95c4; }}

QSlider::groove:horizontal {{ height: 6px; background: #2a2748; border-radius: 3px; }}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 3px; }}
QSlider::handle:horizontal {{ background: #fff; border: 3px solid {ACCENT}; width: 14px; height: 14px; margin: -8px 0; border-radius: 10px; }}

QListWidget {{ background: transparent; border: none; outline: none; }}
QListWidget::item {{ border-radius: 10px; margin: 3px 0; }}
QListWidget::item:hover {{ background: #1a1640; }}
QListWidget::item:selected {{ background: {ACCENT_DARK}; }}

QScrollBar:vertical {{ background: transparent; width: 8px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #2f2a58; border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QMenu {{ background: #16132e; border: 1px solid #2c2754; padding: 6px; }}
QMenu::item {{ padding: 8px 22px; border-radius: 6px; }}
QMenu::item:selected {{ background: {ACCENT_DARK}; }}
QMessageBox {{ background: #12102a; }}
"""
