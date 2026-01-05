"""
Editor window classes for data and executable editing.
"""
import re
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QWidget, QLabel, QScrollArea, QGridLayout, QSizePolicy, QLineEdit)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
import requests
import os

from utils.constants import APPLICATION_NAME, DATA_KEYS, EXE_KEYS, DATA_HEADINGS, EXE_HEADINGS, APP_ICON_PATH
from utils.helpers import confirm
from ui.components.data_table import build_data_table


class Editor(QMainWindow):
    """Editor window for data and executable configuration."""
    
    def __init__(self, editor_type: str, parent, load_data_func, save_data_func, 
                 get_struc_func, refresh_tab_func, pick_path_func, web_profile):
        """
        Initialize editor window.
        
        Args:
            editor_type: Type of editor ("data" or "exe")
            parent: Parent window
            load_data_func: Function to load data
            save_data_func: Function to save data
            get_struc_func: Function to get structure from layout
            refresh_tab_func: Function to refresh tabs
            pick_path_func: Function to pick file paths
            web_profile: QWebEngineProfile for web views
        """
        super().__init__(parent)
        self.type = editor_type
        self.resize(1500, 900)
        self.setWindowTitle(f"{APPLICATION_NAME} Editor")
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        self.load_data_func = load_data_func
        self.save_data_func = save_data_func
        self.get_struc_func = get_struc_func
        self.refresh_tab_func = refresh_tab_func
        self.pick_path_func = pick_path_func
        self.web_profile = web_profile
        
        self.editor = QWidget(self)
        self.setCentralWidget(self.editor)
        self._build_ui()

    def _build_ui(self):
        """Build the editor UI."""
        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addWidget(getattr(self, self.type)())
        self.editor.setLayout(mainlayout)

    def data(self):
        """Create data editor view."""
        items = self.load_data_func(["meta", "recent"])
        return self._create_editor_view(items, DATA_KEYS, DATA_HEADINGS, "meta")

    def exe(self):
        """Create executable editor view."""
        items = self.load_data_func(["ui"])
        return self._create_editor_view((items[0],), EXE_KEYS, EXE_HEADINGS, "ui")

    def _create_editor_view(self, items, keys, headings, save_key):
        """Create a generic editor view."""
        ult = QVBoxLayout()
        ult.setContentsMargins(0, 0, 0, 0)

        # Button row
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

        # Grid layout for data
        layout = QGridLayout()
        layout.setSpacing(50)
        layout.setContentsMargins(10, 10, 10, 30)
        ult.addLayout(layout)

        # Headings
        heading_font = QFont()
        heading_font.setBold(True)
        
        for i, heading in enumerate(headings):
            label = QLabel(heading)
            label.setFont(heading_font)
            label.setFixedHeight(30)
            layout.addWidget(label, 0, i)

        # Build data table
        build_data_table(keys, layout, items, "edit", self, 
                        self.pick_path_func)

        # Connect save button
        def save_action():
            self.save_data_func(items[0], self.get_struc_func(keys[0], layout, items), save_key, "no_merge")
        
        btn_save.clicked.connect(
            lambda: (confirm(parent=self, message="Save changes?", 
                           action=save_action, default="Yes"), self.updater())
        )
        
        # Scroll area
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
        """Update parent window when closing."""
        self.close()
        if self.parent():
            parent_window = self.parent()
            if hasattr(parent_window, 'tabs'):
                if self.type == "data": 
                    index = 1
                elif self.type == "exe": 
                    index = 2
                else:
                    return
                
                from ui.data_view import create_data_view
                if self.type == "data":
                    view = create_data_view(parent_window, self.load_data_func, 
                                          self.save_data_func, self.get_struc_func,
                                          self.refresh_tab_func, self.pick_path_func,
                                          self.web_profile)
                else:
                    view = create_data_view(parent_window, self.load_data_func, 
                                          self.save_data_func, self.get_struc_func,
                                          self.refresh_tab_func, self.pick_path_func,
                                          self.web_profile, view_type="exe")
                
                self.refresh_tab_func(parent_window.tabs, index, view)

    def pick_img_view(self, game):
        """Open web view to pick game image."""
        game_parts = re.split(" ", game)
        game_url = "+".join(game_parts)
        url = f"https://www.steamgriddb.com/search/grids?term={game_url}"
        self.viewer = WebCaptureView(url, game, self, self.web_profile, 
                                     self.refresh_tab_func, self.load_data_func)
        self.viewer.setWindowModality(Qt.WindowModality.NonModal)
        self.viewer.show()


class WebCaptureView(QMainWindow):
    """Web view for capturing image URLs."""
    
    def __init__(self, url: str, game: str, parent, web_profile, refresh_tab_func, load_data_func):
        super().__init__(parent)
        self.game = game
        self.parent_window = parent
        self.web_profile = web_profile
        self.refresh_tab_func = refresh_tab_func
        self.load_data_func = load_data_func
        
        self.resize(1500, 900)
        self.setWindowTitle("Copy Image Address")
        self.setWindowIcon(QIcon(APP_ICON_PATH))

        self.viewer = QWebEngineView(self)
        self.setCentralWidget(self.viewer)

        self.page = QWebEnginePage(web_profile, self.viewer)
        self.viewer.setPage(self.page)

        QTimer.singleShot(0, lambda: self.viewer.load(QUrl(url)))

    def manual_download_window(self):
        """Open manual download window."""
        self.next = ManualDownloadWindow(self.game, self.parent_window, 
                                        self.refresh_tab_func, self.load_data_func)
        self.next.show()

    def closeEvent(self, event):
        """Handle window close event."""
        event.accept()
        self.manual_download_window()
        self.deleteLater()


class ManualDownloadWindow(QMainWindow):
    """Window for manually entering image URL."""
    
    def __init__(self, game: str, parent, refresh_tab_func, load_data_func):
        super().__init__(parent)
        self.game = game
        self.refresh_tab_func = refresh_tab_func
        self.load_data_func = load_data_func
        
        self.resize(300, 200)
        self.setWindowTitle("Paste Image Address")
        self.setWindowIcon(QIcon(APP_ICON_PATH))

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.enterer = QWidget(self)
        self.setCentralWidget(self.enterer)

        self._build_ui()

    def _build_ui(self):
        """Build the UI."""
        mainlayout = QVBoxLayout(self.enterer)
        mainlayout.setContentsMargins(10, 10, 10, 10)
        
        self.d_button = QPushButton("Download")
        self.address_field = QLineEdit()

        mainlayout.addWidget(self.address_field)
        mainlayout.addWidget(self.d_button)

        self.d_button.clicked.connect(self.download)

        self.enterer.setLayout(mainlayout)

    def download(self):
        """Download image from URL."""
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

        self.updater()

    def updater(self):
        """Update parent window."""
        self.close()
        parent_window = self.parent()
        if parent_window and hasattr(parent_window, 'tabs'):
            from ui.data_view import create_data_view
            from ui.library_view import create_library_view
            
            # Refresh exe tab (index 2)
            exe_view = create_data_view(parent_window, self.load_data_func, None, 
                                       None, self.refresh_tab_func, None, None, "exe")
            self.refresh_tab_func(parent_window.tabs, 2, exe_view)
            
            # Refresh library tab (index 0)
            library_view = create_library_view(parent_window, self.load_data_func, None)
            self.refresh_tab_func(parent_window.tabs, 0, library_view)