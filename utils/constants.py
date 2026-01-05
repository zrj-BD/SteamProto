"""
Application constants and configuration values.
"""
import os

# Application metadata
APPLICATION_NAME = "Steam Proto v1.0a"

# File paths
META_DEFAULT = os.path.join(os.getcwd(), "_metadata")
METADATA_DEFAULT = os.path.join(META_DEFAULT, "metadata.json")
RECENTS_FILE_DEFAULT = os.path.join(META_DEFAULT, "recents.json")
UI_FILE_DEFAULT = os.path.join(META_DEFAULT, "ui.json")
SETTINGS_FILE_DEFAULT = os.path.join(META_DEFAULT, "settings.json")
STATE_FILE_DEFAULT = os.path.join(META_DEFAULT, "state.json")

# Image asset paths
ICON_CHECK_PATH = "data/local/check_DATA.png"
ICON_X_PATH = "data/local/x_DATA.png"
APP_ICON_PATH = "data/local/icon_DATA.png"

# UI Constants
GAME_CARD_WIDTH = 250
GAME_CARD_HEIGHT = 375
GAME_CARDS_PER_ROW = 5
GAME_LABEL_FONT_SIZE = 20
PLAY_BUTTON_WIDTH = 100
PLAY_BUTTON_HEIGHT = 50

# Layout spacing
GRID_SPACING = 40
BUTTON_ROW_SPACING = 0
STANDARD_BUTTON_WIDTH = 100

# Settings configuration
SETTINGS_CONFIG = [
    {"key": "automatic_scans", "type": "toggle", "label": "Automatic Scans", "default": False},
    {"key": "scan_frequency", "type": "select", "label": "Scan Frequency", "default": "weekly", "options": ["daily", "weekly", "biweekly", "monthly"]},
    {"key": "design", "type": "toggle", "label": "Design", "default": False},
]

# Data keys
DATA_KEYS = (
    ["appid", "emulator", "build", "date"],
    ["build", "date"]
)

EXE_KEYS = (
    ["exesrc", "png"],
    []
)

DATA_HEADINGS = [
    "Game", "AppID", "Emulator", "Last Build", "Last Date", "Newest Build", "Newest Date"
]

EXE_HEADINGS = [
    "Game", "exesrc", "png", "", "", "", ""
]