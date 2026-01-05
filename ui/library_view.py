"""
Library view for displaying game cards.
"""
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QWidget, 
                              QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt

from utils.constants import GAME_CARDS_PER_ROW, GAME_CARD_WIDTH, GAME_CARD_HEIGHT, GRID_SPACING
from ui.components.game_card import GameCard
from utils.helpers import run_exe


def create_library_view(parent_window, load_data_func, save_data_func, theme_manager):
    """
    Create the library view with game cards.
    
    Args:
        parent_window: Parent window instance
        load_data_func: Function to load data
        theme_manager: Theme manager instance
        
    Returns:
        QScrollArea containing the library view
    """
    games = load_data_func(["ui"])[0]

    ult = QVBoxLayout()
    ult.setContentsMargins(0, 0, 0, 0)

    # Button row
    button_row = QHBoxLayout()
    button_row.setSpacing(0)
    
    btn_refresh = QPushButton("Refresh")
    btn_refresh.setFixedWidth(100)
    button_row.addWidget(btn_refresh)
    
    def refresh_library():
        from utils.helpers import refresh_tab
        refresh_tab(parent_window.tabs, 0, 
                   create_library_view(parent_window, load_data_func, theme_manager))
    
    btn_refresh.clicked.connect(refresh_library)
    
    button_row.addStretch(1)
    
    btn_settings = QPushButton("Settings")
    btn_settings.setFixedWidth(100)
    button_row.addWidget(btn_settings)
    
    def open_settings():
        from ui.settings_window import Settings
        from utils.helpers import refresh_tab
        parent_window.settings = Settings(
            parent_window, load_data_func, save_data_func,
            theme_manager, refresh_tab
        )
        parent_window.settings.show()
    
    btn_settings.clicked.connect(open_settings)
    ult.addLayout(button_row)

    # Grid layout for game cards
    layout = QGridLayout()
    layout.setSpacing(GRID_SPACING)
    layout.setContentsMargins(10, 10, 10, 30)
    ult.addLayout(layout)
    
    row = 0
    col = 0
    
    for game_name in games:
        image_path = f"data/imgs/{game_name}.png"
        exe_path = games[game_name].get("exesrc")
        
        game_card = GameCard(
            game_name=game_name,
            image_path=image_path,
            exe_path=exe_path,
            run_exe_func=run_exe,
            theme_manager=theme_manager,
            parent_window=parent_window,
            width=GAME_CARD_WIDTH,
            height=GAME_CARD_HEIGHT
        )
        
        layout.addWidget(game_card, row, col)
        col += 1
        
        if col == GAME_CARDS_PER_ROW:
            col = 0
            row += 1

    # Scroll area
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    page = QWidget()
    page.setLayout(ult)
    scroll.setWidget(page)
    
    return scroll