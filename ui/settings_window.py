"""
Settings window class.
"""
from typing import Dict, Any
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QWidget, QLabel, QLineEdit, QComboBox, QGridLayout, QSizePolicy)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from PyQt6_SwitchControl import SwitchControl

from utils.constants import APPLICATION_NAME, SETTINGS_CONFIG, APP_ICON_PATH
from utils.helpers import confirm


class Settings(QMainWindow):
    """Settings window for application configuration."""
    
    def __init__(self, parent, load_data_func, save_data_func, theme_manager, refresh_tab_func):
        """
        Initialize settings window.
        
        Args:
            parent: Parent window
            load_data_func: Function to load data
            save_data_func: Function to save data
            theme_manager: Theme manager instance
            refresh_tab_func: Function to refresh tabs
        """
        super().__init__(parent)
        self.resize(1500, 900)
        self.setWindowTitle(f"{APPLICATION_NAME} Settings")
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        self.settings_widgets: Dict[str, Any] = {}
        self.loaded_settings_data = {}
        self.parent_window = parent
        self.theme_manager = theme_manager
        self.load_data_func = load_data_func
        self.save_data_func = save_data_func
        self.refresh_tab_func = refresh_tab_func
        
        self.main_window = self._build_settings_ui()
        self.setCentralWidget(self.main_window)

    def _build_settings_ui(self):
        """Build the settings UI."""
        settings_data = self.load_data_func(["settings"])[0]
        self.loaded_settings_data = settings_data

        ult = QVBoxLayout()
        ult.setContentsMargins(0, 0, 0, 0)
        ult.setSpacing(0)
        ult.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Button row
        button_row = QHBoxLayout()
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

        # Settings grid
        layout = QGridLayout()
        layout.setSpacing(50)
        layout.setContentsMargins(10, 10, 10, 30)
        ult.addLayout(layout)

        bold_font = QFont()
        bold_font.setBold(True)
        
        # Generate settings UI
        for row, setting_config in enumerate(SETTINGS_CONFIG):
            key = setting_config["key"]
            label_text = setting_config["label"]
            setting_type = setting_config["type"]
            default_value = setting_config.get("default", False if setting_type == "toggle" else "")
            
            current_value = settings_data.get(key, default_value)
            
            # Label
            label = QLabel(label_text)
            label.setFont(bold_font)
            label.setFixedSize(200, 50)
            layout.addWidget(label, row, 0)
            
            # Widget based on type
            if setting_type == "toggle":
                widget = self._create_toggle_widget(key, current_value)
            elif setting_type == "text":
                widget = self._create_text_widget(current_value)
            elif setting_type == "select":
                widget = self._create_select_widget(setting_config, current_value, default_value)
            
            layout.addWidget(widget, row, 3)
            self.settings_widgets[key] = widget

        # Connect save button
        def save_and_update():
            new_settings = self.read_settings()
            self.save_data_func(self.loaded_settings_data, new_settings, "settings")
            if "design" in new_settings:
                self.theme_manager.set_theme(new_settings["design"])
            self.close()
        
        btn_save.clicked.connect(
            lambda: confirm(parent=self, message="Save changes?", 
                          action=save_and_update, default="Yes")
        )
        
        page = QWidget()
        page.setLayout(ult)
        page.setMaximumWidth(1500)
        page.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        return page
    
    def _create_toggle_widget(self, key: str, current_value: bool):
        """Create a toggle switch widget."""
        is_checked = bool(current_value)
        widget = SwitchControl(checked=is_checked)
        
        toggle_colors = self.theme_manager.get_toggle_colors()
        button_default_colors = self.theme_manager._button_palette
        
        if key == "design":
            widget.set_bg_color(toggle_colors["bg_color"])
            widget.set_active_color(toggle_colors["active_color"])
            widget.set_circle_color(toggle_colors["circle_color"])
        else:
            widget.set_bg_color(toggle_colors["bg_color"])
            widget.set_active_color(toggle_colors["active_color"])
            widget.set_circle_color(
                button_default_colors["button_on"] if is_checked 
                else button_default_colors["button_off"]
            )
        
        widget.toggled.connect(lambda state, w=widget, k=key: self.on_toggle(state, w, k))
        return widget
    
    def _create_text_widget(self, current_value):
        """Create a text input widget."""
        widget = QLineEdit()
        widget.setText(str(current_value) if current_value is not None else "")
        widget.setMaximumWidth(200)
        widget.setFixedHeight(40)
        return widget
    
    def _create_select_widget(self, setting_config: Dict, current_value, default_value):
        """Create a dropdown select widget."""
        widget = QComboBox()
        options = setting_config.get("options", [])
        widget.addItems(options)
        
        current_str = str(current_value) if current_value is not None else str(default_value)
        if current_str in options:
            widget.setCurrentText(current_str)
        else:
            widget.setCurrentText(str(default_value))
        
        widget.setMaximumWidth(200)
        widget.setFixedHeight(40)
        return widget
    
    def on_toggle(self, state: bool, button: SwitchControl, key: str):
        """Handler for toggle button state changes."""
        toggle_colors = self.theme_manager.get_toggle_colors()
        button_default_colors = self.theme_manager._button_palette
        
        if key == "design":
            button.set_bg_color(toggle_colors["bg_color"])
            button.set_active_color(toggle_colors["active_color"])
            button.set_circle_color(toggle_colors["circle_color"])
            self.theme_manager.set_theme(state)
            self._update_all_toggle_colors()
        else:
            button.set_bg_color(toggle_colors["bg_color"])
            button.set_active_color(toggle_colors["active_color"])
            button.set_circle_color(
                button_default_colors["button_on"] if state 
                else button_default_colors["button_off"]
            )
    
    def _update_all_toggle_colors(self):
        """Update all toggle button colors to match current theme."""
        for key, widget in self.settings_widgets.items():
            if isinstance(widget, SwitchControl):
                is_checked = widget.isChecked()
                toggle_colors = self.theme_manager.get_toggle_colors()
                button_default_colors = self.theme_manager._button_palette
                
                if key == "design":
                    widget.set_bg_color(toggle_colors["bg_color"])
                    widget.set_active_color(toggle_colors["active_color"])
                    widget.set_circle_color(toggle_colors["circle_color"])
                else:
                    widget.set_bg_color(toggle_colors["bg_color"])
                    widget.set_active_color(toggle_colors["active_color"])
                    widget.set_circle_color(
                        button_default_colors["button_on"] if is_checked 
                        else button_default_colors["button_off"]
                    )
    
    def updater(self):
        """Update parent window when closing."""
        self.theme_manager.set_theme(self.loaded_settings_data["design"])
        if self.parent_window and hasattr(self.parent_window, 'tabs'):
            from ui.library_view import create_library_view
            self.refresh_tab_func(
                self.parent_window.tabs, 0, 
                create_library_view(self.parent_window, self.load_data_func, self.theme_manager)
            )

    def closeEvent(self, event):
        """Handle window close event."""
        self.updater()
        event.accept()

    def read_settings(self) -> Dict[str, Any]:
        """Read current values from all settings widgets."""
        settings_dict = {}
        for setting_config in SETTINGS_CONFIG:
            key = setting_config["key"]
            setting_type = setting_config["type"]
            widget = self.settings_widgets.get(key)
            
            if widget is None:
                continue
                
            if setting_type == "toggle":
                settings_dict[key] = bool(widget.isChecked())
            elif setting_type == "text":
                settings_dict[key] = str(widget.text())
            elif setting_type == "select":
                settings_dict[key] = str(widget.currentText())
        
        return settings_dict