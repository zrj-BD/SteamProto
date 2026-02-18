"""
Settings window class.
"""
from typing import Dict, Any
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
                              QWidget, QLabel, QLineEdit, QComboBox, QGridLayout, QSizePolicy, QListWidget, QListWidgetItem)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6_SwitchControl import SwitchControl

from utils.constants import APPLICATION_NAME, SETTINGS_CONFIG, APP_ICON_PATH
from utils.helpers import confirm, pick_path

class Settings(QMainWindow):
    """Settings window for application configuration."""
    
    def __init__(self, parent, load_data_func, save_data_func, theme_manager):
        """
        Initialize settings window.
        
        Args:
            parent: Parent window
            load_data_func: Function to load data
            save_data_func: Function to save data
            theme_manager: Theme manager instance
        """
        super().__init__(parent)
        self.resize(1500, 900)
        self.setWindowTitle(f"{APPLICATION_NAME} {self.tr('Settings')}")
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        self.settings_widgets: Dict[str, Any] = {}
        self.loaded_settings_data = {}
        self.parent_window = parent
        self.theme_manager = theme_manager
        self.load_data_func = load_data_func
        self.save_data_func = save_data_func
        
        self.main_window = self._build_settings_ui()
        self.setCentralWidget(self.main_window)

    def _build_settings_ui(self):
        """Build the settings UI."""
        settings_data = self.load_data_func(["settings"])[0]
        self.loaded_settings_data = settings_data
        self.theme = settings_data.get("design", False)
        self.theme_on = settings_data.get("theme_activated", True)

        ult = QVBoxLayout()
        ult.setContentsMargins(0, 0, 0, 0)
        ult.setSpacing(0)
        ult.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Button row
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        
        btn_exit = QPushButton(self.tr("Exit"))
        btn_exit.clicked.connect(lambda: self.close())
        btn_exit.setFixedWidth(100)
        button_row.addWidget(btn_exit)
        
        btn_save = QPushButton(self.tr("Save"))
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
            label_text = self.tr(setting_config["label"])
            setting_type = setting_config["type"]
            default_value = setting_config.get("default", False if setting_type == "toggle" else "")

            current_value = settings_data.get(key, default_value)

            if setting_type == "select":
                current_value = setting_config.get("options", [])[setting_config.get("values", []).index(current_value)]
                current_value = self.tr(current_value) if key != "language" else current_value

            # Label
            label = QLabel(label_text)
            label.setFont(bold_font)
            label.setFixedSize(200, 35)
            label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(label, row, 0, alignment=Qt.AlignmentFlag.AlignTop)

            widget = None

            # Widget based on type
            if setting_type == "toggle":
                widget = self._create_toggle_widget(key, current_value) # type: ignore
            elif setting_type == "text":
                widget = self._create_text_widget(current_value)
            elif setting_type == "select":
                widget = self._create_select_widget(setting_config, current_value, default_value)
            elif setting_type == "list-dirs":
                widget = self._create_list_dirs_widget(key, current_value if isinstance(current_value, list) else [])

            layout.addWidget(widget, row, 3, alignment=Qt.AlignmentFlag.AlignTop)
            self.settings_widgets[key] = widget

        # Connect save button
        def save_and_update():
            old_settings = self.loaded_settings_data.copy()
            new_settings = self.read_settings()
            if old_settings.get("language") != new_settings.get("language"):
                from utils.helpers import restart_script
                import os
                script_path = os.path.join(os.path.dirname(__file__), "..", "window.pyw")
                def a(): return
                lang_changed = confirm(self.parent_window, QCoreApplication.translate("msg", "These changes will require a reset to function."), a, "No")
                print(lang_changed)
                if not lang_changed:
                    new_settings["language"] = old_settings["language"]
                else:
                    self.save_data_func(self.loaded_settings_data, new_settings, "settings")
                    restart_script(script_path)
            else: 
                self.close()
            self.save_data_func(self.loaded_settings_data, new_settings, "settings")
        
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
        options = [self.tr(opt) for opt in options] if setting_config["key"] != "language" else options
        widget.addItems(options)

        current_str = str(current_value) if current_value is not None else str(default_value)
        if current_str in options:
            widget.setCurrentText(current_str)
        else:
            widget.setCurrentText(str(default_value))

        widget.setMaximumWidth(200)
        widget.setFixedHeight(40)
        return widget

    def _create_list_dirs_widget(self, key: str, current_dirs: list):
        """Create a widget for managing list of directories to skip."""
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # List widget to display folders
        list_widget = QListWidget()
        list_widget.setMaximumWidth(400)
        list_widget.setFixedHeight(150)

        # Store the list widget reference for reading values later
        list_widget.key = key  # type: ignore

        def create_item_widget(directory_path):
            """Create a horizontal widget with folder name."""
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(5, 1, 5, 1)
            item_layout.setSpacing(10)

            # Folder name label
            name_label = QLabel(directory_path)
            item_layout.addWidget(name_label, 1)

            item_widget.setLayout(item_layout)
            return item_widget

        # Populate list with current directories
        for directory in current_dirs:
            item = QListWidgetItem()
            item_widget = create_item_widget(directory)

            list_widget.addItem(item)
            item.setSizeHint(item_widget.sizeHint())
            list_widget.setItemWidget(item, item_widget)

        # Button layout for add and remove buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        # Button to add folders
        btn_add = QPushButton(self.tr("Add Folder"))
        btn_add.setFixedHeight(40)
        btn_add.setFixedWidth(100)

        # Button to remove selected
        btn_remove = QPushButton(self.tr("Remove Selected"))
        btn_remove.setFixedHeight(40)
        btn_remove.setFixedWidth(120)

        # Connect add button to pick_path
        def add_folder():
            import os
            # Get game directory (parent of working environment directory)
            game_dir = os.path.dirname(os.getcwd())

            path, selected = pick_path(self, game_dir, type="dir")
            if selected and path != game_dir:
                # Validate that folder is a direct child of game_dir
                parent = os.path.dirname(path) # type: ignore
                if parent != "":
                    return

                # Check if already in list
                existing_items = []
                for i in range(list_widget.count()):
                    item_widget = list_widget.itemWidget(list_widget.item(i))
                    if item_widget:
                        label = item_widget.findChild(QLabel)
                        if label:
                            existing_items.append(label.text())

                if path not in existing_items:
                    item = QListWidgetItem()
                    item_widget = create_item_widget(path)

                    list_widget.addItem(item)
                    item.setSizeHint(item_widget.sizeHint())
                    list_widget.setItemWidget(item, item_widget)

        def remove_selected():
            for item in list_widget.selectedItems():
                list_widget.takeItem(list_widget.row(item))

        btn_add.clicked.connect(add_folder)
        btn_remove.clicked.connect(remove_selected)

        button_layout.addWidget(btn_add)
        button_layout.addWidget(btn_remove)
        button_layout.addStretch()

        layout.addWidget(list_widget)
        layout.addLayout(button_layout)

        container.setLayout(layout)
        # Store list widget reference for reading later
        container.list_widget = list_widget  # type: ignore

        return container
    
    def on_toggle(self, state: bool, button: SwitchControl, key: str):
        """Handler for toggle button state changes."""
        toggle_colors = self.theme_manager.get_toggle_colors()
        button_default_colors = self.theme_manager._button_palette

        if key == "design":
            self.theme = state
            self.theme_manager.set_theme(self.theme, self.theme_on)
            self._update_all_toggle_colors()
            self.parent_window.refresh(full=True)
        elif key == "theme_activated":
            self.theme_on = state
            self.theme_manager.set_theme(self.theme, self.theme_on)
            self._update_all_toggle_colors()
            self.parent_window.refresh(full=True)
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
                elif key != "design":
                    widget.set_bg_color(toggle_colors["bg_color"])
                    widget.set_active_color(toggle_colors["active_color"])
                    widget.set_circle_color(
                        button_default_colors["button_on"] if is_checked 
                        else button_default_colors["button_off"]
                    )
    
    def updater(self):
        """Update parent window when closing."""
        self.theme_manager.set_theme(self.loaded_settings_data.get("design", False), self.loaded_settings_data.get("theme_activated", True))
        self.parent_window.refresh(full=True)

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
                options = setting_config.get("options", [])
                options = [self.tr(opt) for opt in options] if setting_config["key"] != "language" else options
                settings_dict[key] = setting_config.get("values", [])[options.index(widget.currentText())]
            elif setting_type == "list-dirs":
                # Extract directories from the list widget
                list_widget = widget.list_widget  # type: ignore
                dirs = [list_widget.item(i).text() for i in range(list_widget.count())]
                settings_dict[key] = dirs

        return settings_dict