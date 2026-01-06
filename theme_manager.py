"""
Theme Manager Module
Handles dark/light mode theming for the Steam Proto application.
"""
from typing import Dict, Any
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal as Signal


class ThemeManager(QObject):
    """
    Centralized theme manager for the application.
    Manages dark and light mode stylesheets and provides theme switching functionality.
    """
    
    # Signal emitted when theme changes
    theme_changed = Signal(bool)  # True for light mode, False for dark mode
    theme_on = Signal(bool)
    
    def __init__(self):
        super().__init__()
        self._is_light_mode = False
        self._activated_theme = False
        
        # Define color palettes
        self._dark_palette = {
            "window_bg": "#1e1e1e",
            "widget_bg": "#2d2d2d",
            "button_bg": "#3d3d3d",
            "button_hover": "#4d4d4d",
            "button_pressed": "#5d5d5d",
            "text": "#ffffff",
            "text_secondary": "#b0b0b0",
            "border": "#404040",
            "accent": "#0078d4",
            "accent_hover": "#005a9e",
            "label_overlay": "rgba(0, 0, 0, 150)",
            "label_overlay_hover": "rgba(0, 0, 0, 200)",
            "tab_bg": "#252525",
            "tab_selected": "#3d3d3d",
        }
        
        self._light_palette = {
            "window_bg": "#f5f5f5",
            "widget_bg": "#ffffff",
            "button_bg": "#e0e0e0",
            "button_hover": "#d0d0d0",
            "button_pressed": "#c0c0c0",
            "text": "#000000",
            "text_secondary": "#505050",
            "border": "#c0c0c0",
            "accent": "#0078d4",
            "accent_hover": "#005a9e",
            "label_overlay": "rgba(255, 255, 255, 200)",
            "label_overlay_hover": "rgba(255, 255, 255, 240)",
            "tab_bg": "#e8e8e8",
            "tab_selected": "#ffffff",
        }

        self._button_palette = {
            "button_on": "#59B659",
            "button_off": "#AA3E3E"
        }
    
    @property
    def is_light_mode(self) -> bool:
        """Check if light mode is currently active."""
        return self._is_light_mode
    
    @property
    def activated_theme(self) -> bool:
        """Check if theme is currently active."""
        return self._activated_theme

    @property
    def palette(self) -> Dict[str, str]:
        """Get current color palette."""
        return self._light_palette if self._is_light_mode else self._dark_palette
    
    def set_theme(self, is_light_mode: bool, activated_theme: bool = True):
        """
        Set the application theme.
        
        Args:
            is_light_mode: True for light mode, False for dark mode
            activated_theme: True for theme on, False for theme off
        """
        if self._is_light_mode != is_light_mode or self._activated_theme != activated_theme:
            self._is_light_mode = is_light_mode
            self._activated_theme = activated_theme
            self.apply_theme()
            self.theme_changed.emit(is_light_mode)
            self.theme_on.emit(activated_theme)
    
    def apply_theme(self):
        """Apply the current theme to the QApplication."""
        app = QApplication.instance()
        if app is None:
            return
        
        palette = self.palette
        
        # Main application stylesheet
        stylesheet = f"""
        QMainWindow {{
            background-color: {palette["window_bg"]};
            color: {palette["text"]};
        }}
        
        QWidget {{
            background-color: {palette["widget_bg"]};
            color: {palette["text"]};
        }}
        
        QPushButton {{
            background-color: {palette["button_bg"]};
            color: {palette["text"]};
            border: 1px solid {palette["border"]};
            border-radius: 4px;
            padding: 5px 15px;
            min-height: 25px;
        }}
        
        QPushButton:hover {{
            background-color: {palette["button_hover"]};
        }}
        
        QPushButton:pressed {{
            background-color: {palette["button_pressed"]};
        }}
        
        QLabel {{
            color: {palette["text"]};
            background-color: transparent;
        }}
        
        QLineEdit {{
            background-color: {palette["widget_bg"]};
            color: {palette["text"]};
            border: 1px solid {palette["border"]};
            border-radius: 3px;
            padding: 5px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {palette["accent"]};
        }}
        
        QComboBox {{
            background-color: {palette["widget_bg"]};
            color: {palette["text"]};
            border: 1px solid {palette["border"]};
            border-radius: 3px;
            padding: 5px;
        }}
        
        QComboBox:hover {{
            background-color: {palette["button_hover"]};
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {palette["widget_bg"]};
            color: {palette["text"]};
            selection-background-color: {palette["accent"]};
            selection-color: {palette["text"]};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {palette["border"]};
            background-color: {palette["tab_bg"]};
        }}
        
        QTabBar::tab {{
            background-color: {palette["tab_bg"]};
            color: {palette["text"]};
            border: 1px solid {palette["border"]};
            padding: 8px 20px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {palette["tab_selected"]};
            border-bottom: 2px solid {palette["accent"]};
        }}
        
        QTabBar::tab:hover {{
            background-color: {palette["button_hover"]};
        }}
        
        QScrollArea {{
            border: none;
            background-color: {palette["window_bg"]};
        }}
        
        QScrollBar:vertical {{
            background-color: {palette["widget_bg"]};
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {palette["button_bg"]};
            min-height: 20px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {palette["button_hover"]};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QMessageBox {{
            background-color: {palette["widget_bg"]};
            color: {palette["text"]};
        }}
        
        QMessageBox QLabel {{
            color: {palette["text"]};
        }}
        
        QMessageBox QPushButton {{
            min-width: 80px;
        }}
        """
        if self._activated_theme:
            app.setStyleSheet(stylesheet)  # type: ignore[attr-defined]
        else:
            app.setStyleSheet(None)  # type: ignore[attr-defined]
    
    def get_game_label_style(self) -> str:
        """Get stylesheet for game labels in library view."""
        if self._activated_theme:
            palette = self.palette
        else: 
            palette = self._dark_palette
        return f"background-color: {palette['label_overlay']}; color: {palette['text']}; border-radius: 5px;"
    
    def get_play_button_style(self) -> str:
        """Get stylesheet for play buttons in library view."""
        if self._activated_theme:
            palette = self.palette
        else: 
            palette = self._dark_palette
        return f"""
            QPushButton {{
                background-color: {palette['label_overlay']};
                color: {palette['text']};
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {palette['label_overlay_hover']};
            }}
            QPushButton:pressed {{
                background-color: {palette['button_pressed']};
            }}
            """
    
    def get_toggle_colors(self) -> Dict[str, str]:
        """
        Get toggle button colors based on theme mode.
        
        Args:
            is_light_mode: True for light mode theme, False for dark mode theme
            
        Returns:
            Dictionary with bg_color, active_color, and circle_color
        """
        if self._is_light_mode and self._activated_theme:
            # Light mode: light background, slightly lighter when toggled on
            return {
                "bg_color": "#E5E5E5",  # Light gray background (off state)
                "active_color": "#F5F5F5",
                "circle_color": "#FFD700"
            }
        else:
            # Dark mode: dark background, slightly lighter when toggled on
            return {
                "bg_color": "#3d3d3d",  # Dark background (off state)
                "active_color": "#4d4d4d",
                "circle_color": "#666666"
            }


# Global theme manager instance
_theme_manager: ThemeManager | None = None


def get_theme_manager() -> ThemeManager:
    """Get or create the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

