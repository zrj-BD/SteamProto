"""
Main application window.
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

from utils.constants import APPLICATION_NAME, APP_ICON_PATH
from ui.library_view import create_library_view
from ui.data_view import create_data_view


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""
    
    def __init__(self, load_data_func, save_data_func, get_struc_func,
                 theme_manager, refresh_tab_func, pick_path_func):
        """
        Initialize main window.
        
        Args:
            load_data_func: Function to load data
            save_data_func: Function to save data
            get_struc_func: Function to get structure from layout
            theme_manager: Theme manager instance
            refresh_tab_func: Function to refresh tabs
            pick_path_func: Function to pick file paths
        """
        super().__init__()
        self.resize(1500, 900)
        self.setWindowTitle(APPLICATION_NAME)
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        
        self.load_data_func = load_data_func
        self.save_data_func = save_data_func
        self.get_struc_func = get_struc_func
        self.theme_manager = theme_manager
        self.refresh_tab_func = refresh_tab_func
        self.pick_path_func = pick_path_func
        
        # Load and apply initial theme
        settings_data = load_data_func(["settings"])[0]
        is_light = bool(settings_data.get("design", False))
        activated_theme = bool(settings_data.get("theme_activated", True))
        theme_manager.set_theme(is_light, activated_theme)

        # Cache fonts for performance
        self._bold_font = QFont()
        self._bold_font.setBold(True)
        self._game_label_font = QFont()
        self._game_label_font.setBold(True)
        self._game_label_font.setPixelSize(20)
        
        self.main_window = QWidget(self)
        self.setCentralWidget(self.main_window)

        self._build_ui()

    def _build_ui(self):
        """Build the main UI with tabs."""
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Add tabs
        self.tabs.addTab(self._create_library_tab(), "Library")
        self.tabs.addTab(self._create_data_tab(), "Data")
        self.tabs.addTab(self._create_exe_tab(), "Data 2")
        
        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addWidget(self.tabs)
        self.main_window.setLayout(mainlayout)

    def _create_library_tab(self):
        """Create the library tab."""
        return create_library_view(self, self.load_data_func, self.save_data_func, self.theme_manager)

    def _create_data_tab(self):
        """Create the data/metadata tab."""
        return create_data_view(
            self, self.load_data_func, self.save_data_func,
            self.get_struc_func, self.refresh_tab_func,
            self.pick_path_func, "data"
        )

    def _create_exe_tab(self):
        """Create the executable data tab."""
        return create_data_view(
            self, self.load_data_func, self.save_data_func,
            self.get_struc_func, self.refresh_tab_func,
            self.pick_path_func, "exe"
        )