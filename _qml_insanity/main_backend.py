"""
Main Python backend for QML Steam Proto application
Exposes data and functionality to QML frontend
"""
import sys
import json
import os
from typing import Dict, Any, List, Optional
import argparse
from datetime import datetime, date
import subprocess
import time
import re
import requests

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QUrl
from PyQt6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQuick import QQuickView
from PyQt6.QtWebEngineQuick import QtWebEngineQuick

# Import your existing modules
import web
import remover
import main

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

# Constants
META_DEFAULT = os.path.join(os.path.dirname(os.getcwd()), "_metadata")
METADATA_DEFAULT = os.path.join(META_DEFAULT, "metadata.json")
RECENTS_FILE_DEFAULT = os.path.join(META_DEFAULT, "recents.json")
UI_FILE_DEFAULT = os.path.join(META_DEFAULT, "ui.json")
SETTINGS_FILE_DEFAULT = os.path.join(META_DEFAULT, "settings.json")
STATE_FILE_DEFAULT = os.path.join(META_DEFAULT, "state.json")
DATA_LOC = os.path.join(os.path.dirname(os.getcwd()), "data")

APPLICATION_NAME = "Steam Proto v1.0a"


class DataManager(QObject):
    """Handles all data loading/saving operations"""
    
    dataChanged = pyqtSignal()
    
    def __init__(self, args):
        super().__init__()
        self.args = args
        self._metadata = {}
        self._recents = {}
        self._ui_data = {}
        self._settings = {}
        self._state = {}
        self.load_all_data()
    
    def load_all_data(self):
        """Load all JSON files"""
        self._metadata = self._load_file(self.args.metadata)
        self._recents = self._load_file(self.args.recentdata)
        self._ui_data = self._load_file(self.args.uidata)
        self._settings = self._load_file(self.args.settingsdata)
        self._state = self._load_file(self.args.statedata)
        self.dataChanged.emit()
    
    def _load_file(self, path: str) -> Dict[str, Any]:
        """Load a single JSON file"""
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    return json.load(fh)
            except Exception:
                pass
        return {}
    
    def _save_file(self, path: str, data: Dict[str, Any]):
        """Save data to JSON file"""
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=True)
    
    @pyqtSlot(str, result=str)
    def getMetadataJson(self, game: str) -> str:
        """Get metadata for a specific game as JSON string"""
        return json.dumps(self._metadata.get(game, {}))
    
    @pyqtSlot(result=str)
    def getAllGamesJson(self) -> str:
        """Get all games from UI data as JSON"""
        return json.dumps(list(self._ui_data.keys()))
    
    @pyqtSlot(result=str)
    def getMetadataListJson(self) -> str:
        """Get all metadata as JSON for data view"""
        result = []
        for game, data in self._metadata.items():
            item = {"game": game}
            item.update(data)
            # Add recent data if available
            if game in self._recents:
                item["recent_build"] = self._recents[game].get("build", "")
                item["recent_date"] = self._recents[game].get("date", 0)
            result.append(item)
        return json.dumps(result)
    
    @pyqtSlot(result=str)
    def getUiDataListJson(self) -> str:
        """Get UI data list as JSON"""
        result = []
        for game, data in self._ui_data.items():
            item = {"game": game}
            item.update(data)
            item["has_image"] = os.path.exists(f"{DATA_LOC}/imgs/{game}.png")
            result.append(item)
        return json.dumps(result)
    
    @pyqtSlot(str, result=str)
    def getGameImage(self, game: str) -> str:
        """Get image path for a game"""
        path = f"{DATA_LOC}/imgs/{game}.png"
        if os.path.exists(path):
            return f"file:///{os.path.abspath(path)}"
        return ""
    
    @pyqtSlot(str, result=str)
    def getGameExePath(self, game: str) -> str:
        """Get executable path for a game"""
        return self._ui_data.get(game, {}).get("exesrc", "")
    
    @pyqtSlot(str, str)
    def updateMetadata(self, game: str, json_data: str):
        """Update metadata for a game"""
        data = json.loads(json_data)
        if game not in self._metadata:
            self._metadata[game] = {}
        self._metadata[game].update(data)
        self._save_file(self.args.metadata, self._metadata)
        self.dataChanged.emit()
    
    @pyqtSlot(str, str)
    def updateUiData(self, game: str, json_data: str):
        """Update UI data for a game"""
        data = json.loads(json_data)
        if game not in self._ui_data:
            self._ui_data[game] = {}
        self._ui_data[game].update(data)
        self._save_file(self.args.uidata, self._ui_data)
        self.dataChanged.emit()
    
    @pyqtSlot(result=str)
    def getSettingsJson(self) -> str:
        """Get all settings as JSON"""
        return json.dumps(self._settings)
    
    @pyqtSlot(str)
    def saveSettings(self, json_data: str):
        """Save settings from JSON"""
        data = json.loads(json_data)
        self._settings.update(data)
        self._save_file(self.args.settingsdata, self._settings)
        self.dataChanged.emit()
    
    @pyqtSlot(str, result=bool)
    def getSetting(self, key: str) -> bool:
        """Get a specific setting"""
        return self._settings.get(key, False)


class GameLauncher(QObject):
    """Handles game launching"""
    
    launchError = pyqtSignal(str)
    gameLaunched = pyqtSignal()
    
    @pyqtSlot(str)
    def launchGame(self, exe_path: str):
        """Launch a game executable"""
        if not exe_path or not os.path.exists(exe_path):
            self.launchError.emit("Executable not found")
            return
        
        try:
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
            self.gameLaunched.emit()
        except Exception as e:
            self.launchError.emit(f"Error launching game: {str(e)}")


class ScanManager(QObject):
    """Handles scanning and updating operations"""
    
    scanStarted = pyqtSignal()
    scanFinished = pyqtSignal()
    scanError = pyqtSignal(str)
    
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager
    
    @pyqtSlot()
    def performScan(self):
        """Perform a scan operation"""
        self.scanStarted.emit()
        try:
            main.main()
            self.data_manager.load_all_data()
            self.scanFinished.emit()
        except Exception as e:
            self.scanError.emit(f"Scan error: {str(e)}")
    
    @pyqtSlot()
    def performUpdate(self):
        """Perform an update operation"""
        self.scanStarted.emit()
        try:
            web.main()
            self.data_manager.load_all_data()
            self.scanFinished.emit()
        except Exception as e:
            self.scanError.emit(f"Update error: {str(e)}")
    
    @pyqtSlot()
    def performRescan(self):
        """Perform a full rescan"""
        self.scanStarted.emit()
        try:
            remover.main()
            main.main()
            self.data_manager.load_all_data()
            self.scanFinished.emit()
        except Exception as e:
            self.scanError.emit(f"Rescan error: {str(e)}")


class ImageDownloader(QObject):
    """Handles image downloading"""
    
    downloadStarted = pyqtSignal()
    downloadFinished = pyqtSignal()
    downloadError = pyqtSignal(str)
    
    @pyqtSlot(str, str)
    def downloadImage(self, url: str, game: str):
        """Download an image from URL"""
        self.downloadStarted.emit()
        
        if not url.lower().endswith((".png", ".jpg")):
            self.downloadError.emit("Invalid image URL")
            return
        
        path = f"{DATA_LOC}/imgs/{game}.png"
        try:
            if os.path.exists(path):
                os.remove(path)
            
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            
            with open(path, "wb") as f:
                f.write(r.content)
            
            self.downloadFinished.emit()
        except Exception as e:
            self.downloadError.emit(f"Download failed: {str(e)}")
    
    @pyqtSlot(str, result=str)
    def getSearchUrl(self, game: str) -> str:
        """Get Steam Grid DB search URL for a game"""
        game_parts = re.split(" ", game)
        game_url = "+".join(game_parts)
        return f"https://www.steamgriddb.com/search/grids?term={game_url}"


def create_blank(loc: str):
    """Create a blank JSON file"""
    with open(loc, "w", encoding="utf-8") as fh:
        json.dump({}, fh, indent=2, ensure_ascii=True)


if __name__ == "__main__":
    # Parse arguments
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", "-m", default=METADATA_DEFAULT)
    p.add_argument("--recentdata", "-r", default=RECENTS_FILE_DEFAULT)
    p.add_argument("--uidata", "-ui", default=UI_FILE_DEFAULT)
    p.add_argument("--settingsdata", "-settings", default=SETTINGS_FILE_DEFAULT)
    p.add_argument("--statedata", "-state", default=STATE_FILE_DEFAULT)
    args = p.parse_args()
    
    # Initialize files if needed
    if not os.path.exists(args.metadata):
        main.main()
        web.main()
    if not os.path.exists(args.uidata):
        create_blank(args.uidata)
    if not os.path.exists(args.settingsdata):
        create_blank(args.settingsdata)
    if not os.path.exists(args.statedata):
        create_blank(args.statedata)

    # Initialize QtWebEngine
    QtWebEngineQuick.initialize()
    
    # Create application
    app = QGuiApplication(sys.argv)
    
    # Create backend objects
    data_manager = DataManager(args)
    game_launcher = GameLauncher()
    scan_manager = ScanManager(data_manager)
    image_downloader = ImageDownloader()
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Expose objects to QML
    engine.rootContext().setContextProperty("dataManager", data_manager)
    engine.rootContext().setContextProperty("gameLauncher", game_launcher)
    engine.rootContext().setContextProperty("scanManager", scan_manager)
    engine.rootContext().setContextProperty("imageDownloader", image_downloader)
    engine.rootContext().setContextProperty("appName", APPLICATION_NAME)
    
    # Load main QML file
    engine.load(QUrl.fromLocalFile("main.qml"))
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec())
