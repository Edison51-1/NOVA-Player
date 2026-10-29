"""Génère assets/icon.png et assets/icon.ico à partir du logo vectoriel."""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PySide6.QtGui import QGuiApplication  # noqa: E402
import icons  # noqa: E402

app = QGuiApplication([])
out = ROOT / "assets"
out.mkdir(exist_ok=True)
png = out / "icon.png"
icons.logo_pixmap(512).save(str(png))

from PIL import Image  # noqa: E402
Image.open(png).save(out / "icon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("Icônes générées dans", out)
