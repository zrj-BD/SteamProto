from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from utils.constants import ICON_CHECK_PATH, ICON_X_PATH

def _scaled(path: str, size=40):
    return QPixmap(path).scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

CHECK_PIX = _scaled(ICON_CHECK_PATH)
X_PIX = _scaled(ICON_X_PATH)