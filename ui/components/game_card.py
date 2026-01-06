"""
Reusable game card widget component.
"""
import os
from typing import Optional, Callable
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt


class GameCard(QWidget):
    """A card widget displaying a game with image, title, and play button."""
    
    def __init__(
        self, 
        game_name: str, 
        image_path: Optional[str] = None,
        exe_path: Optional[str] = None,
        run_exe_func: Optional[Callable] = None,
        theme_manager = None,
        parent_window = None,
        width: int = 250,
        height: int = 375
    ):
        """
        Initialize a game card.
        
        Args:
            game_name: Name of the game
            image_path: Path to game image (optional)
            exe_path: Path to game executable (optional)
            run_exe_func: Function to run executable
            theme_manager: Theme manager for styling
            parent_window: Parent window reference
            width: Card width
            height: Card height
        """
        super().__init__()
        self.game_name = game_name
        self.image_path = image_path
        self.exe_path = exe_path
        self.run_exe_func = run_exe_func
        self.theme_manager = theme_manager
        self.parent_window = parent_window
        
        self.setFixedSize(width, height)
        self._setup_ui(width, height)
    
    def _setup_ui(self, width: int, height: int):
        """Set up the card's UI components."""
        # Container for image
        image_label = QLabel(self)
        
        # Load and display image
        if self.image_path and os.path.exists(self.image_path):
            image = QPixmap(self.image_path)
        else:
            # Placeholder if image doesn't exist
            image = QPixmap(width, height)
            image.fill(Qt.GlobalColor.gray)
        
        image = image.scaled(
            width, height, 
            Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
            Qt.TransformationMode.SmoothTransformation
        )
        image_label.setPixmap(image)
        image_label.setGeometry(0, 0, width, height)
        
        # Game name label
        name_label = QLabel(self.game_name)
        if self.theme_manager:
            name_label.setStyleSheet(self.theme_manager.get_game_label_style())
        
        font = QFont()
        font.setBold(True)
        font.setPixelSize(20)
        name_label.setFont(font)
        name_label.setWordWrap(True)
        
        # Play button
        play_button = QPushButton("Play")
        play_button.setFixedSize(100, 50)
        if self.theme_manager:
            play_button.setStyleSheet(self.theme_manager.get_play_button_style())
        
        # Connect play button
        if self.exe_path and self.run_exe_func:
            play_button.clicked.connect(
                lambda: self.run_exe_func(self.exe_path, self.parent_window)  # pyright: ignore[reportOptionalCall]
            )
        
        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(
            name_label, 
            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        layout.addWidget(
            play_button, 
            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
        )