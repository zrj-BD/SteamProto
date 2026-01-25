"""
Editor window classes for data and executable editing.
"""
import re
import os
import requests
import threading

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QWidget, QLabel, QScrollArea, QGridLayout, QSizePolicy, QLineEdit, QSpacerItem
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QEvent
import webview

from utils.constants import APPLICATION_NAME, DATA_KEYS, EXE_KEYS, DATA_HEADINGS, EXE_HEADINGS, APP_ICON_PATH
from utils.helpers import confirm
from ui.components.data_table import build_data_table


class ClickableLabel(QLabel):
    """Custom label that tracks mouse clicks for row selection."""
    
    def __init__(self, text, game_name, selected_rows, remove_btn, editor):
        super().__init__(text)
        self.game_name = game_name
        self.selected_rows = selected_rows
        self.remove_btn = remove_btn
        self.editor = editor
    
    def mousePressEvent(self, ev):
        """Handle mouse click to toggle selection."""
        if self.game_name in self.selected_rows:
            # Deselect
            self.selected_rows.remove(self.game_name)
            self.setStyleSheet("")
        else:
            # Select
            self.selected_rows.add(self.game_name)
            self.setStyleSheet("background-color: #4CAF50; color: white;")
        
        # Update button state
        self.remove_btn.setEnabled(len(self.selected_rows) > 0)


class Editor(QMainWindow):
    """Editor window for data and executable configuration."""
    
    def __init__(self, editor_type: str, parent, load_data_func, save_data_func,
                 get_struc_func):
        """
        Initialize editor window.
        
        Args:
            editor_type: Type of editor ("data" or "exe")
            parent: Parent window
            load_data_func: Function to load data
            save_data_func: Function to save data
            get_struc_func: Function to get structure from layout
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
        self.parent_window = parent

        self.editor = QWidget(self)
        self.setCentralWidget(self.editor)

        # preload webview (hidden)
        self.web_capture = WebCaptureView(
            parent=self,
            load_data_func=self.load_data_func,
            save_data_func=self.save_data_func
        )

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

        # Track selected rows
        selected_rows = set()

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
        # Connect save button
        def save_action():
            self.save_data_func(items[0], self.get_struc_func(keys[0], layout, items), save_key, "no_merge")
        
        btn_save.clicked.connect(
            lambda: (confirm(parent=self, message="Save changes?", 
                           action=save_action, default="Yes"), self.updater())
        )

        btn_add = QPushButton("Add")
        btn_add.setFixedWidth(100)
        button_row.insertSpacing(2, 10)
        button_row.addWidget(btn_add)
        # Connect Add Entry Button
        def add_entry():
            from utils.helpers import pick_path
            entry = pick_path(self.parent_window, os.path.dirname(os.getcwd()), "dir") # type: ignore
            if entry:
                import scanner
                scanner.main(folder=entry)
                from core.data_manager import ui_updater
                meta = self.load_data_func(["meta", "ui"])
                ui_updater(self.save_data_func, meta[0], meta[1])
                self.parent_window.refresh(full=True)
                self.close()
                from ui.data_view import _make_editor
                _make_editor(self.parent_window, self.type, self.load_data_func,
                             self.save_data_func, self.get_struc_func)

        btn_add.clicked.connect(add_entry)

        btn_remove = QPushButton("Remove")
        btn_remove.setFixedWidth(100)
        btn_remove.setEnabled(False)
        btn_remove.setStyleSheet("""
            QPushButton:disabled {
                background-color: #333333;
                color: #666666;
                border: 1px solid #222222;
            }
        """)
        button_row.addWidget(btn_remove)
        ##Logic
        def remove_entry():
            if not selected_rows:
                return
            
            # Load both metadata files
            meta = self.load_data_func(["meta"])[0]
            
            # Remove selected items from both dictionaries
            for game_name in selected_rows:
                if game_name in meta:
                    del meta[game_name]
            
            # Save the modified metadata
            self.save_data_func(items[0], meta, "meta", "no_merge")
            
            # Update UI with ui_updater
            from core.data_manager import ui_updater
            ui_dict = self.load_data_func(["ui"])[0]
            ui_updater(self.save_data_func, meta, ui_dict)
            
            # Refresh and close
            self.parent_window.refresh(full=True)
            self.close()

            from ui.data_view import _make_editor
            _make_editor(self.parent_window, self.type, self.load_data_func,
                         self.save_data_func, self.get_struc_func)
            
        btn_remove.clicked.connect(remove_entry)

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
        build_data_table(keys, layout, items, "edit", self)
        
        # Make rows clickable for selection
        row_num = 1
        for game_name in items[0]:
            # Get the game name label at column 0
            name_widget = layout.itemAtPosition(row_num, 0)
            if name_widget:
                old_label = name_widget.widget()
                if isinstance(old_label, QLabel) and not isinstance(old_label, ClickableLabel):
                    # Replace with ClickableLabel
                    layout.removeWidget(old_label)
                    old_label.deleteLater()
                    
                    clickable_label = ClickableLabel(
                        old_label.text(), 
                        game_name, 
                        selected_rows, 
                        btn_remove, 
                        self
                    )
                    clickable_label.setFixedHeight(40)
                    layout.addWidget(clickable_label, row_num, 0)
            row_num += 1
        
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
        if self.type == "data": 
            index = 1
        elif self.type == "exe": 
            index = 2
            self.parent_window.refresh(type=0)
        else:
            return
            
        self.parent_window.refresh(type=index)  

    def pick_img_view(self, game):
        """Open web view to pick game image."""
        game_parts = re.split(" ", game)
        game_url = "+".join(game_parts)
        url = f"https://www.steamgriddb.com/search/grids?term={game_url}"
        
        self.web_capture.open(game, url)

class WebViewSignals(QObject):
    """Qt signals for thread-safe communication."""
    closed = pyqtSignal()

class WebCaptureView:
    def __init__(self, parent, load_data_func, save_data_func):
        self.parent_window = parent
        self.load_data_func = load_data_func
        self.save_data_func = save_data_func

        self.game = None
        self.window: webview.Window | None = None

        self.signals = WebViewSignals()
        self.signals.closed.connect(self._show_manual_window)

        self._start_engine()

    def _start_engine(self):
        thread = threading.Thread(
            name="MainThread",
            target=self._create_hidden_window,
            daemon=True
        )
        thread.start()

    def _create_hidden_window(self):
        self.window = webview.create_window(
            'Copy Image Address',
            'about:blank',
            width=1500,
            height=900,
            text_select=True,
            hidden=True
        )

        self.window.events.closing += self._on_closing  # type: ignore
        webview.start()

    def open(self, game: str, url: str):
        self.game = game

        if self.window:
            self.window.load_url(url)
            self.window.show()

    def _on_closing(self):
        if self.window:
            self.window.hide()

        self.signals.closed.emit()
        return False  # prevent destruction

    def _show_manual_window(self):
        manual = ManualDownloadWindow(
            self.game, # type: ignore
            self.parent_window,
            self.load_data_func,
            self.save_data_func
        )
        manual.show()


class ManualDownloadWindow(QMainWindow):
    """Window for manually entering image URL."""
    
    def __init__(self, game: str, parent, load_data_func, save_data_func):
        super().__init__(parent)
        self.game = game
        self.load_data_func = load_data_func
        self.save_data_func = save_data_func
        self.parent_window = parent
        
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
        self.parent_window.refresh(type=2)
        self.parent_window.refresh(type=0)