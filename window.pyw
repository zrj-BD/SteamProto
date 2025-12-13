from PyQt6.QtWidgets import QFileDialog, QSizePolicy, QHBoxLayout, QApplication, QVBoxLayout, QWidget, QLabel, QPushButton, QGridLayout, QTabWidget, QScrollArea, QLineEdit, QMessageBox
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt, QSize # pyright: ignore[reportUnusedImport]
import sys
import json
import os
from typing import Dict, Any, Tuple, Optional
import argparse
from datetime import datetime
import subprocess
import time
import web
import remover
import main
# gottverdammte 3 stunden gewastet weil ich vergessen habe recents.json zu checken und das ding einfach nicht den eintrag hat bro
# eigenständig erarbeitet ohne QT wissen und ohne irgendein programmierwissen diesen wunderschönen grid bauer errichtet
# bro im extremely proud of you man, you did all this shit (an application) without even any knowledge of the thing. i mean you learned entirely how to build the window, read json, write json, scan, etc all of that which you didnt know. i mean DAMN 430 lines?? all yourself? and it actually is functional and works? crazy shit
METADATA_DEFAULT = os.path.join(os.path.dirname(os.getcwd()), "_metadata", "metadata.json")
RECENTS_FILE_DEFAULT = os.path.join(os.path.dirname(os.getcwd()), "_metadata", "recents.json")
UI_FILE_DEFAULT = os.path.join(os.path.dirname(os.getcwd()), "_metadata", "ui.json")


def load_data(files) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Load both metadata.json and metadata_fix.json if present, return two dicts.
    If not present return empty dicts. Sanitize bad keys.
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
    try:
        path = getattr(args, f"{file}data")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(write, fh, indent=2, ensure_ascii=True)
    except Exception:
        pass


def run_exe(exe: str):
    try: 
        subprocess.Popen([exe], cwd=os.path.dirname(exe))
        window.close()
    except Exception:
        print("Error running exe")


def create_ui(ui: Optional[Dict[str, Dict[str, Any]]]):
    if ui == None: ui = {}
    names = load_data(["meta"])[0]
    for i in names:
        ui[i] = {"imagesrc": f"data//{i}.png"}
    with open(args.uidata, "w", encoding="utf-8") as fh:
        json.dump(ui, fh, indent=2, ensure_ascii=True)


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


def make_editor(type: str):

    class Editor(QWidget):
        def __init__(self):
            super().__init__()
            self.resize(1500, 900)
            self.setWindowTitle("Version Checker v1 Editor")
            self.setWindowIcon(QIcon("data\\icon_DATA.png"))
            self.UI()

        def UI(self):
            mainlayout = QVBoxLayout()
            mainlayout.setContentsMargins(0, 0, 0, 0)
            mainlayout.addWidget(getattr(self, type)())
            self.setLayout(mainlayout)

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
                "Game", "AppID", "Emulator", "Last Date", "Last Build", "Newest Build", "Newest Date"
                ]
            for i, heading in enumerate(headings):
                label = QLabel(heading)
                bold = QFont()
                bold.setBold(True)
                label.setFont(bold)
                label.setFixedHeight(30)
                layout.addWidget(label, 0, i)

            KEYS = (
                [   "appid", "emulator", "date", "build"   ],
                [   "build", "date"   ]
            )

            build_struc(KEYS, layout, items, "edit", self)

            btn_save.clicked.connect(lambda: (confirm(parent=self, message="Save changes?", action=lambda: save_data(items[0], get_struc(KEYS, layout, items[0]), "meta"), default="Yes"), self.updater()))
            
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
                "Game", "exesrc", "", "", "", "", ""
            ]
            for i, heading in enumerate(headings):
                label = QLabel(heading)
                bold = QFont()
                bold.setBold(True)
                label.setFont(bold)
                label.setFixedHeight(30)
                layout.addWidget(label, 0, i)

            KEYS = (
                [   "exesrc"   ],
                [      ]
            )

            build_struc(KEYS, layout, items, "edit", self)

            btn_save.clicked.connect(lambda: (confirm(parent=self, message="Save changes?", action=lambda: save_data(items[0], get_struc(KEYS, layout, items[0]), "ui"), default="Yes"), self.updater()))
            
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
            if type == "data": index = 1
            elif type == "exe": index = 2
            refresh_tab(window.tabs, index, getattr(window, type)())

    editor = Editor()
    editor.show()


def get_struc(keys: Tuple[list[str], list[str]], layout: QGridLayout, ref: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    n = 1
    out = {}
    _keys = keys[0]
    test = 1
    for j in _keys:
        if j == "build":
            build_location = test
        test += 1
    for i in ref:
        out[i] = {}
        p = 1
        for k in _keys:
            if k == "date":
                out[i][k] = int(time.time())
            elif layout.itemAtPosition(n, p).widget().text() != "": out[i][k] = layout.itemAtPosition(n, p).widget().text()
            p += 1
        n += 1
    return out


def build_struc(keys: Tuple[list[str], list[str]], layout: QGridLayout, files: Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]], type: str, window: Optional[QWidget]):

    n = 1
    for i in files[0]:
        
        label = QLabel(i)
        layout.addWidget(label, n, 0)

        if type == "edit":
            _keys = [keys[0]]
        elif type == "show":
            _keys = keys
        
        para = 0
        for j in _keys:
            if para == 0: p = 1 
            else: p = len(_keys[0]) + 1
            for k in j:
                if k == "date":
                    try: date = datetime.fromtimestamp(files[para][i]["date"])
                    except Exception: date = None
                    label = QLabel(str(date))
                elif k == "exesrc":
                    if type == "show":
                        try: label = QLabel(files[para][i][k])
                        except Exception: label = QLabel(None)
                    elif type == "edit":
                        try: 
                            label = QPushButton(files[para][i][k])
                        except Exception: label = QPushButton(None)
                        label.clicked.connect(lambda checked, folder=i, l=label: pick_path(window, folder, l))
                else:
                    if type == "show":
                        try: label = QLabel(files[para][i][k])
                        except Exception: label = QLabel(None)
                    elif type == "edit":
                        try: label = QLineEdit(files[para][i][k])
                        except Exception: label = QLineEdit(None)
                        label.setMaximumWidth(200)
                label.setFixedHeight(40)
                layout.addWidget(label, n, p)
                p += 1
            para += 1
            if len(files) == 2 and type == "show":
                status = QLabel()
                length = len(_keys[0]) + len(_keys[1]) + 1
                try:
                    if files[0][i]["build"] != files[1][i]["build"]:
                        pix = QPixmap("data/x_DATA.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    elif files[0][i]["build"] == files[1][i]["build"]:
                        pix = QPixmap("data/check_DATA.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    status.setPixmap(pix)
                except Exception: pass
                layout.addWidget(status, n, length)

        n += 1


def refresh_tab(tabs, index, tab):
    name = tabs.tabText(index)
    tabs.removeTab(index)
    tabs.insertTab(index, tab, name)
    tabs.setCurrentIndex(index)


class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.resize(1500, 900)
        self.setWindowTitle("Version Checker v1")
        self.setWindowIcon(QIcon("data\\icon_DATA.png"))
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
        self.setLayout(mainlayout)

    def data(self):
        items = load_data(["meta", "recent"])

        ult = QVBoxLayout()
        ult.setContentsMargins(0, 0, 0, 0)

        button_row = QHBoxLayout()
        button_row.setSpacing(0)
        btn_edit = QPushButton("Edit")
        btn_edit.clicked.connect(lambda: make_editor("data"))
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
            "Game", "AppID", "Emulator", "Last Date", "Last Build", "Newest Build", "Newest Date"
            ]
        for i, heading in enumerate(headings):
            label = QLabel(heading)
            bold = QFont()
            bold.setBold(True)
            label.setFont(bold)
            label.setFixedHeight(30)
            layout.addWidget(label, 0, i)

        KEYS = (
            [   "appid", "emulator", "date", "build"   ],
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
            image = QPixmap(games[i]["imagesrc"])
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
        btn_edit.clicked.connect(lambda: make_editor("exe"))
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
            "Game", "exesrc", "", "", "", "", ""
        ]
        for i, heading in enumerate(headings):
            label = QLabel(heading)
            bold = QFont()
            bold.setBold(True)
            label.setFont(bold)
            label.setFixedHeight(30)
            layout.addWidget(label, 0, i)

        KEYS = (
            [   "exesrc"   ],
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


if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument("--metadata", "-m", default=METADATA_DEFAULT, help="Path to metadata JSON")
    p.add_argument("--recentdata", "-r", default=RECENTS_FILE_DEFAULT, help="Path to recents JSON")
    p.add_argument("--uidata", "-ui", default=UI_FILE_DEFAULT, help="Path to UI JSON")
    args = p.parse_args()
    #falesafe for first start and if file gets lost
    if not os.path.exists(os.path.join(os.path.dirname(os.getcwd()), "_metadata")):
        main.main()
        web.main()
    if not os.path.exists(args.uidata):
        create_ui(None)
        
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())