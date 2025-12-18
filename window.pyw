##Imports
# PyQt6
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QSizePolicy, QHBoxLayout, QApplication, QVBoxLayout, QWidget, QLabel, QPushButton, QGridLayout, QTabWidget, QScrollArea, QLineEdit, QMessageBox
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineUrlRequestInterceptor
# random
import sys
import json
import os
from typing import Dict, Any, List, Tuple, Optional
import argparse
from datetime import datetime
import subprocess
import time
import re
import requests
# programs
import web
import remover
import main
# bro im extremely proud of you man, you did all this shit (an application) without even any knowledge of the thing. i mean you learned entirely how to build the window, read json, write json, scan, etc all of that which you didnt know. i mean DAMN 430 lines?? all yourself? and it actually is functional and works? crazy shit
##file locations
META_DEFAULT = os.path.join(os.getcwd(), "_metadata")
METADATA_DEFAULT = os.path.join(META_DEFAULT, "metadata.json")
RECENTS_FILE_DEFAULT = os.path.join(META_DEFAULT, "recents.json")
UI_FILE_DEFAULT = os.path.join(META_DEFAULT, "ui.json")
###loading data

def load_data(files) -> Tuple[Dict[str, Dict[str, Any]], Optional[Dict[str, Dict[str, Any]]]]:
    """
    Load both files and return dicts.
    """
    list = []
    for i in files:
        data: Dict[str, Any]
        data = {}
        path = getattr(args, f"{i}data")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception:
                pass
        list.append(data)
    return tuple(list)


def save_data(og, data, file):
    def merge(og, data):
        for key, value in data.items():
            if isinstance(value, dict) and key in og and isinstance(og[key], dict):
                merge(og[key], value)
            else:
                og[key] = value
        return og
    write = merge(og, data)
    path = getattr(args, f"{file}data")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(write, fh, indent=2, ensure_ascii=True)


def create_ui(ui: Optional[Dict[str, Dict[str, Any]]]):
    if ui == None: ui = {}
    with open(args.uidata, "w", encoding="utf-8") as fh:
        json.dump(ui, fh, indent=2, ensure_ascii=True)
##running files

def run_exe(exe: str):
    try: 
        subprocess.Popen([exe], cwd=os.path.dirname(exe))
        window.close()
    except Exception:
        print("Error running exe")
##struc build

def get_struc(keys: List[str], layout: QGridLayout, ref: Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    n = 1
    out = {}
    for i in ref[0]:
        out[i] = {}
        p = 1
        for k in keys:
            if k == "build":
                build = layout.itemAtPosition(n, p).widget().text()  # type: ignore
            if k == "date":
                if build == ref[1][i]["build"] or build == "":
                    out[i][k] = int(time.time())
                else:
                    out[i][k] = ref[0][i]["date"]
            elif layout.itemAtPosition(n, p).widget().text() != "": out[i][k] = layout.itemAtPosition(n, p).widget().text()  # type: ignore
            p += 1
        n += 1
    return out


def build_struc(keys: Tuple[list[str], list[str]], layout: QGridLayout, files: Tuple[Dict[str, Dict[str, Any]], Optional[Dict[str, Dict[str, Any]]]], type: str, window: Optional[QWidget]):

    n = 1
    for i in files[0]:
        
        label = QLabel(i)
        layout.addWidget(label, n, 0)

        if type == "edit":
            _keys = [keys[0]]
        elif type == "show":
            _keys = keys
        
        para = 0
        for j in _keys: # pyright: ignore[reportPossiblyUnboundVariable]
            if para == 0: p = 1 
            else: p = len(_keys[0]) + 1 # pyright: ignore[reportPossiblyUnboundVariable]
            for k in j:
                if k == "date":
                    try: date = datetime.fromtimestamp(files[para][i]["date"]) # pyright: ignore[reportOptionalSubscript]
                    except Exception: date = None
                    label = QLabel(str(date))
                elif k == "exesrc":
                    if type == "show":
                        try: label = QLabel(files[para][i][k]) # pyright: ignore[reportOptionalSubscript]
                        except Exception: label = QLabel(None)
                    elif type == "edit":
                        try: 
                            label = QPushButton(files[para][i][k]) # pyright: ignore[reportOptionalSubscript]
                        except Exception: label = QPushButton(None)
                        label.clicked.connect(lambda checked, folder=i, l=label: pick_path(window, folder, l))
                elif k == "png":
                    if type == "show":
                        label = QLabel()
                        if os.path.exists(f"data/imgs/{i}.png"):
                            pix = QPixmap("data/local/check_DATA.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        else:
                            pix = QPixmap("data/local/x_DATA.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        label.setPixmap(pix)
                    if type == "edit":
                        label = QWidget()
                        label.setContentsMargins(0, 0, 0, 0)
                        label_layout = QHBoxLayout()
                        if os.path.exists(f"data/imgs/{i}.png"):
                            pix = QPixmap("data/local/check_DATA.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        else:
                            pix = QPixmap("data/local/x_DATA.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        image = QLabel()
                        image.setPixmap(pix)
                        button = QPushButton("Change/Add")
                        try:
                            button.clicked.connect(lambda checked, game = i: Editor("exe", window).pick_img_view(game))
                        except Exception: pass
                        label_layout.addWidget(image)
                        label_layout.addWidget(button)                  
                        label.setLayout(label_layout)
                else:
                    if type == "show":
                        try: label = QLabel(files[para][i][k]) # pyright: ignore[reportOptionalSubscript]
                        except Exception: label = QLabel(None)
                    elif type == "edit":
                        try: label = QLineEdit(files[para][i][k]) # pyright: ignore[reportOptionalSubscript]
                        except Exception: label = QLineEdit(None)
                        label.setMaximumWidth(200)
                if not (k == "png" and type == "edit"): label.setFixedHeight(40)
                layout.addWidget(label, n, p)
                p += 1
            para += 1
            if len(files) == 2 and type == "show":
                status = QLabel()
                length = len(_keys[0]) + len(_keys[1]) + 1 # pyright: ignore[reportPossiblyUnboundVariable]
                try:
                    if files[0][i]["build"] == files[1][i]["build"]: # pyright: ignore[reportOptionalSubscript]
                        pix = QPixmap("data/local/check_DATA.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    else:
                        pix = QPixmap("data/local/x_DATA.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    status.setPixmap(pix)
                except Exception: pass
                layout.addWidget(status, n, length)

        n += 1


def refresh_tab(tabs, index, tab):
    name = tabs.tabText(index)
    tabs.removeTab(index)
    tabs.insertTab(index, tab, name)
    tabs.setCurrentIndex(index)
##windows

def confirm(parent: QWidget, message: str, action, default):
    msg_box = QMessageBox(parent)
    msg_box.resize(400, 200)
    msg_box.setWindowTitle("Confirm Action")
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(getattr(QMessageBox.StandardButton, default))
    
    result = msg_box.exec()  # modal; waits for user
    if result == QMessageBox.StandardButton.Yes:
        action()


def pick_path(window, folder, label):
    path, _ = QFileDialog.getOpenFileName(
        window,
        "Select EXE",
        os.path.join(os.path.dirname(os.getcwd()), folder),
        "Executable Files (*.exe);;All Files (*)"
    )
    if path:
        label.setText(path)


class ManualDownloadWindow(QMainWindow):
    game: str
    
    def __init__(self, game, parent):
        super().__init__(parent)
        self.game = game
        self.resize(300, 200)
        self.setWindowTitle("Paste Image Address")
        self.setWindowIcon(QIcon("data\\local\\icon_DATA.png"))

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.enterer = QWidget(self)
        self.setCentralWidget(self.enterer)

        self.UI()

    def UI(self):
        mainlayout = QVBoxLayout(self.enterer)
        mainlayout.setContentsMargins(10, 10, 10, 10)
        
        self.d_button = QPushButton("Download")
        self.address_field = QLineEdit()

        mainlayout.addWidget(self.address_field)
        mainlayout.addWidget(self.d_button)

        self.d_button.clicked.connect(self.download)

        self.enterer.setLayout(mainlayout)

    def download(self):
        url = self.address_field.text().strip()
        if not url.lower().endswith(".png") and not url.lower().endswith(".jpg"):
            return
        
        path = f"data/imgs/{self.game}.png"
        if os.path.exists(path):
            os.remove(path)
        r = requests.get(url, timeout=15)
        r.raise_for_status()

        with open(path, "wb") as f:
            f.write(r.content)

        self.close()

    def updater(self):
        refresh_tab(window.tabs, 2, getattr(window, "exe")())
        refresh_tab(window.tabs, 0, getattr(window, "library")())

    def closeEvent(self, event):
        self.updater()
        event.accept()


class WebCaptureView(QMainWindow):
    url: str
    game: str

    def __init__(self, url, game, parent):
        super().__init__(parent)
        self.game = game
        self.parent1 = parent
        self.resize(1500, 900)
        self.setWindowTitle("Copy Image Address")
        self.setWindowIcon(QIcon("data\\local\\icon_DATA.png"))

        self.viewer = QWebEngineView(self)
        self.setCentralWidget(self.viewer)

        self.page = QWebEnginePage(profile, self.viewer)
        self.viewer.setPage(self.page)

        QTimer.singleShot(0, lambda: self.viewer.load(QUrl(url)))

    def manual_download_window(self):
        self.next = ManualDownloadWindow(self.game, self.parent1)
        self.next.show()

    def closeEvent(self, event):
        self.hide()
        self.manual_download_window()


class Editor(QMainWindow):
    type: str

    def __init__(self, type, parent):
        super().__init__(parent)
        self.type = type
        self.resize(1500, 900)
        self.setWindowTitle("Version Checker v1 Editor")
        self.setWindowIcon(QIcon("data\\local\\icon_DATA.png"))
        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.editor = QWidget(self)
        self.setCentralWidget(self.editor)

        self.UI()

    def UI(self):
        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addWidget(getattr(self, self.type)())
        self.editor.setLayout(mainlayout)

    def data(self):
        items = load_data(["meta", "recent"])

        ult = QVBoxLayout()
        ult.setContentsMargins(0, 0, 0, 0)

        button_row = QHBoxLayout()
        button_row.setSpacing(0)
        button_row.setContentsMargins(0, 0, 0, 0)
        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(lambda: self.updater())
        btn_exit.setFixedWidth(100)
        button_row.addWidget(btn_exit)
        btn_save = QPushButton("Save")
        btn_save.setFixedWidth(100)
        button_row.addWidget(btn_save)
        button_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ult.addLayout(button_row)

        layout = QGridLayout()
        layout.setSpacing(50)
        layout.setContentsMargins(10, 10, 10, 30) #links oben rechts unten
        ult.addLayout(layout)

        headings = [
            "Game", "AppID", "Emulator", "Last Build", "Last Date", "Newest Build", "Newest Date"
            ]
        for i, heading in enumerate(headings):
            label = QLabel(heading)
            bold = QFont()
            bold.setBold(True)
            label.setFont(bold)
            label.setFixedHeight(30)
            layout.addWidget(label, 0, i)

        KEYS = (
            [   "appid", "emulator", "build", "date"   ],
            [   "build", "date"   ]
        )

        build_struc(KEYS, layout, items, "edit", self)

        btn_save.clicked.connect(lambda: (confirm(parent=self, message="Save changes?", action=lambda: save_data(items[0], get_struc(KEYS[0], layout, items), "meta"), default="Yes"), self.updater())) # pyright: ignore[reportArgumentType]
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        page = QWidget()
        page.setLayout(ult)
        page.setMaximumWidth(1500)
        page.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        scroll.setWidget(page)
        return scroll

    def exe(self):
        items = load_data(["ui"])

        ult = QVBoxLayout()
        ult.setContentsMargins(0, 0, 0, 0)

        button_row = QHBoxLayout()
        button_row.setSpacing(0)
        button_row.setContentsMargins(0, 0, 0, 0)
        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(lambda: self.updater())
        btn_exit.setFixedWidth(100)
        button_row.addWidget(btn_exit)
        btn_save = QPushButton("Save")
        btn_save.setFixedWidth(100)
        button_row.addWidget(btn_save)
        button_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ult.addLayout(button_row)

        layout = QGridLayout()
        layout.setSpacing(50)
        layout.setContentsMargins(10, 10, 10, 30) #links oben rechts unten
        ult.addLayout(layout)

        headings = [
            "Game", "exesrc", "png", "", "", "", ""
        ]
        for i, heading in enumerate(headings):
            label = QLabel(heading)
            bold = QFont()
            bold.setBold(True)
            label.setFont(bold)
            label.setFixedHeight(30)
            layout.addWidget(label, 0, i)

        KEYS = (
            [   "exesrc", "png"   ],
            [      ]
        )

        build_struc(KEYS, layout, items, "edit", self)

        btn_save.clicked.connect(lambda: (confirm(parent=self, message="Save changes?", action=lambda: save_data(items[0], get_struc(KEYS[0], layout, items), "ui"), default="Yes"), self.updater())) # pyright: ignore[reportArgumentType]
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        page = QWidget()
        page.setLayout(ult)
        page.setMaximumWidth(1500)
        page.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        scroll.setWidget(page)
        return scroll
    
    def updater(self):
        self.close()
        if self.type == "data": index = 1
        elif self.type == "exe": index = 2
        refresh_tab(window.tabs, index, getattr(window, self.type)())  # pyright: ignore[reportPossiblyUnboundVariable]

    def pick_img_view(self, game):
        game_parts = re.split(" ", game)
        game_url = ""
        for i in game_parts:
            game_url += i + "+"
        game_url = game_url[:-1]
        url = f"https://www.steamgriddb.com/search/grids?term={game_url}"
        self.viewer = WebCaptureView(url, game, self)
        self.viewer.setWindowModality(Qt.WindowModality.NonModal)
        self.viewer.show()

    def closeEvent(self, event):
        self.updater()
        event.accept()
##main

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1500, 900)
        self.setWindowTitle("Version Checker v1")
        self.setWindowIcon(QIcon("data\\local\\icon_DATA.png"))
        self.main_window = QWidget(self)
        self.setCentralWidget(self.main_window)
        self.UI()

    def UI(self):
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.addTab(self.library(), "Library")
        self.tabs.addTab(self.data(), "Data")
        self.tabs.addTab(self.exe(), "Data 2")
        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addWidget(self.tabs)
        self.main_window.setLayout(mainlayout)

    def data(self):
        items = load_data(["meta", "recent"])

        ult = QVBoxLayout()
        ult.setContentsMargins(0, 0, 0, 0)

        button_row = QHBoxLayout()
        button_row.setSpacing(0)
        btn_edit = QPushButton("Edit")
        btn_edit.clicked.connect(lambda: self.make_editor("data"))
        btn_edit.setFixedWidth(100)
        button_row.addWidget(btn_edit)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setFixedWidth(100)
        button_row.addWidget(btn_refresh)
        btn_refresh.clicked.connect(lambda: refresh_tab(self.tabs, 1, self.data()))
        btn_update = QPushButton("Update")
        btn_update.setFixedWidth(100)
        button_row.addWidget(btn_update)
        btn_update.clicked.connect(lambda: (web.main(), refresh_tab(self.tabs, 1, self.data())))
        btn_scan = QPushButton("Scan")
        btn_scan.setFixedWidth(100)
        button_row.addWidget(btn_scan)
        btn_scan.clicked.connect(lambda: (main.main(), refresh_tab(self.tabs, 1, self.data())))
        btn_rescan = QPushButton("Rescan")
        btn_rescan.setFixedWidth(100)
        button_row.addWidget(btn_rescan)
        btn_rescan.clicked.connect(lambda: (confirm(parent=self, message="This will reset also the fixed_metadata. Only do this if there had been an error previously. Continue?", action=lambda: (remover.main(), main.main(), refresh_tab(self.tabs, 1, self.data())), default="No")))
        button_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ult.addLayout(button_row)

        layout = QGridLayout()
        layout.setSpacing(50)
        layout.setContentsMargins(10, 10, 10, 30) #links oben rechts unten
        ult.addLayout(layout)

        headings = [
            "Game", "AppID", "Emulator", "Last Build", "Last Date", "Newest Build", "Newest Date"
            ]
        for i, heading in enumerate(headings):
            label = QLabel(heading)
            bold = QFont()
            bold.setBold(True)
            label.setFont(bold)
            label.setFixedHeight(30)
            layout.addWidget(label, 0, i)

        KEYS = (
            [   "appid", "emulator", "build", "date"   ],
            [   "build", "date"   ]
        )

        build_struc(KEYS, layout, items, "show", None)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        page = QWidget()
        page.setLayout(ult)
        page.setMaximumWidth(1500)
        page.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        scroll.setWidget(page)
        return scroll

    def library(self):
        games = load_data(["ui"])[0]

        ult = QVBoxLayout()
        ult.setContentsMargins(0, 0, 0, 0)

        button_row = QHBoxLayout()
        button_row.setSpacing(0)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setFixedWidth(100)
        button_row.addWidget(btn_refresh)
        btn_refresh.clicked.connect(lambda: refresh_tab(self.tabs, 0, self.library()))
        button_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ult.addLayout(button_row)

        layout = QGridLayout()
        layout.setSpacing(40)
        layout.setContentsMargins(10, 10, 10, 30)
        ult.addLayout(layout)
        
        row = 0
        n = 0
        for i in games:
            container = QWidget()
            #container.setStyleSheet("border: 2px solid black; background-color: lightgray;")
            image_l = QLabel(container)
            image = QPixmap(f"data/imgs/{i}.png")
            image = image.scaled(250, 375, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            image_l.setPixmap(image)
            image_l.setGeometry(0, 0, 250, 375)

            label = QLabel(i)
            bold = QFont()
            bold.setBold(True)
            bold.setPixelSize(20)
            label.setStyleSheet("background-color: rgba(0, 0, 0, 100)")
            label.setFont(bold)
            label.setWordWrap(True)

            button = QPushButton("Play")
            button.setFixedSize(100, 50)
            button.setStyleSheet("""QPushButton{ background-color: rgba(0, 0, 0, 100)}
                                 QPushButton:hover{ background-color: rgba(0, 0, 0, 150)}
                                 QPushButton:pressed{ background-color: rgba(0, 0, 0, 200)}""")
            try: 
                exe_path = games[i]["exesrc"]
                button.clicked.connect(lambda checked, path=exe_path: run_exe(path))
            except Exception: pass

            container.setFixedHeight(375)
            container.setFixedWidth(250)
            container_layout = QVBoxLayout()
            container.setLayout(container_layout)
            container_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            container_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

            layout.addWidget(container, row, n)
            n += 1
            if n == 5:
                n = 0
                row += 1

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        page = QWidget()
        page.setLayout(ult)
        scroll.setWidget(page)
        return scroll
    
    def exe(self):
        items = load_data(["ui"])

        ult = QVBoxLayout()
        ult.setContentsMargins(0, 0, 0, 0)

        button_row = QHBoxLayout()
        button_row.setSpacing(0)
        button_row.setContentsMargins(0, 0, 0, 0)
        btn_edit = QPushButton("Edit")
        btn_edit.clicked.connect(lambda: self.make_editor("exe"))
        btn_edit.setFixedWidth(100)
        button_row.addWidget(btn_edit)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setFixedWidth(100)
        button_row.addWidget(btn_refresh)
        btn_refresh.clicked.connect(lambda: refresh_tab(self.tabs, 2, self.exe()))
        button_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ult.addLayout(button_row)

        layout = QGridLayout()
        layout.setSpacing(50)
        layout.setContentsMargins(10, 10, 10, 30) #links oben rechts unten
        ult.addLayout(layout)

        headings = [
            "Game", "exesrc", "png", "", "", "", ""
        ]
        for i, heading in enumerate(headings):
            label = QLabel(heading)
            bold = QFont()
            bold.setBold(True)
            label.setFont(bold)
            label.setFixedHeight(30)
            layout.addWidget(label, 0, i)

        KEYS = (
            [   "exesrc", "png"   ],
            [      ]
        )

        build_struc(KEYS, layout, items, "show", None)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        page = QWidget()
        page.setLayout(ult)
        page.setMaximumWidth(1500)
        page.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        scroll.setWidget(page)
        return scroll

    def make_editor(self, type):
        self.editor = Editor(type, self)
        self.editor.show()
##execution

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument("--metadata", "-m", default=METADATA_DEFAULT, help="Path to metadata JSON")
    p.add_argument("--recentdata", "-r", default=RECENTS_FILE_DEFAULT, help="Path to recents JSON")
    p.add_argument("--uidata", "-ui", default=UI_FILE_DEFAULT, help="Path to UI JSON")
    args = p.parse_args()
    #falesafe for first start and if file gets lost
    if not os.path.exists(args.metadata):
        main.main()
        web.main()
    if not os.path.exists(args.uidata):
        create_ui(None)

    app = QApplication(sys.argv)

    profile = QWebEngineProfile("main")
    # profile.setPersistentStoragePath("web/web_profile")
    # profile.setCachePath("web/web_cache")
    profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
    profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
    profile.setHttpUserAgent(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36")

    window = Window()
    window.show()
    sys.exit(app.exec())


##TODO:
#library functions:
#search function
#favourites function
#sort function