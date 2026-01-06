"""
Data view for displaying game metadata and executable information.
"""
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QWidget, 
                              QLabel, QScrollArea, QGridLayout, QSizePolicy)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from utils.constants import DATA_KEYS, EXE_KEYS, DATA_HEADINGS, EXE_HEADINGS
from utils.helpers import confirm
from ui.components.data_table import build_data_table


def create_data_view(parent_window, load_data_func, save_data_func, get_struc_func,
                     refresh_tab_func, pick_path_func, web_profile, view_type="data"):
    """
    Create a data view (either metadata or executable view).
    
    Args:
        parent_window: Parent window instance
        load_data_func: Function to load data
        save_data_func: Function to save data
        get_struc_func: Function to get structure from layout
        refresh_tab_func: Function to refresh tabs
        pick_path_func: Function to pick file paths
        web_profile: QWebEngineProfile for web views
        view_type: Type of view ("data" or "exe")
        
    Returns:
        QScrollArea containing the data view
    """
    if view_type == "data":
        return _create_metadata_view(parent_window, load_data_func, save_data_func,
                                     get_struc_func, refresh_tab_func, pick_path_func,
                                     web_profile)
    else:
        return _create_exe_view(parent_window, load_data_func, save_data_func,
                               get_struc_func, refresh_tab_func, pick_path_func,
                               web_profile)


def _create_metadata_view(parent_window, load_data_func, save_data_func,
                          get_struc_func, refresh_tab_func, pick_path_func,
                          web_profile):
    """Create the metadata data view."""
    items = load_data_func(["meta", "recent"])

    ult = QVBoxLayout()
    ult.setContentsMargins(0, 0, 0, 0)

    # Button row
    button_row = QHBoxLayout()
    button_row.setSpacing(0)
    
    btn_edit = QPushButton("Edit")
    btn_edit.clicked.connect(lambda: _make_editor(parent_window, "data", load_data_func,
                                                   save_data_func, get_struc_func,
                                                   refresh_tab_func, pick_path_func,
                                                   web_profile))
    btn_edit.setFixedWidth(100)
    button_row.addWidget(btn_edit)
    
    btn_refresh = QPushButton("Refresh")
    btn_refresh.setFixedWidth(100)
    button_row.addWidget(btn_refresh)
    btn_refresh.clicked.connect(
        lambda: refresh_tab_func(parent_window.tabs, 1, 
                                create_data_view(parent_window, load_data_func,
                                               save_data_func, get_struc_func,
                                               refresh_tab_func, pick_path_func,
                                               web_profile, "data"))
    )
    
    btn_update = QPushButton("Update")
    btn_update.setFixedWidth(100)
    button_row.addWidget(btn_update)
    
    def update_action():
        import web
        web.main()
        refresh_tab_func(parent_window.tabs, 1, 
                        create_data_view(parent_window, load_data_func,
                                       save_data_func, get_struc_func,
                                       refresh_tab_func, pick_path_func,
                                       web_profile, "data"))
    
    btn_update.clicked.connect(update_action)
    
    btn_scan = QPushButton("Scan")
    btn_scan.setFixedWidth(100)
    button_row.addWidget(btn_scan)
    
    def scan_action():
        import scanner
        scanner.main()
        refresh_tab_func(parent_window.tabs, 1, 
                        create_data_view(parent_window, load_data_func,
                                       save_data_func, get_struc_func,
                                       refresh_tab_func, pick_path_func,
                                       web_profile, "data"))
    
    btn_scan.clicked.connect(scan_action)
    
    btn_rescan = QPushButton("Rescan")
    btn_rescan.setFixedWidth(100)
    button_row.addWidget(btn_rescan)
    
    def rescan_action():
        import remover
        import scanner
        remover.main()
        scanner.main()
        refresh_tab_func(parent_window.tabs, 1, 
                        create_data_view(parent_window, load_data_func,
                                       save_data_func, get_struc_func,
                                       refresh_tab_func, pick_path_func,
                                       web_profile, "data"))
    
    btn_rescan.clicked.connect(
        lambda: confirm(
            parent=parent_window,
            message="This will reset also the fixed_metadata. Only do this if there had been an error previously. Continue?",
            action=rescan_action,
            default="No"
        )
    )
    
    button_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
    ult.addLayout(button_row)

    # Grid layout
    layout = QGridLayout()
    layout.setSpacing(50)
    layout.setContentsMargins(10, 10, 10, 30)
    ult.addLayout(layout)

    # Headings
    bold_font = QFont()
    bold_font.setBold(True)
    
    for i, heading in enumerate(DATA_HEADINGS):
        label = QLabel(heading)
        label.setFont(bold_font)
        label.setFixedHeight(30)
        layout.addWidget(label, 0, i)

    # Build data table
    build_data_table(DATA_KEYS, layout, items, "show", None)
    
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


def _create_exe_view(parent_window, load_data_func, save_data_func,
                    get_struc_func, refresh_tab_func, pick_path_func,
                    web_profile):
    """Create the executable data view."""
    items = load_data_func(["ui"])

    ult = QVBoxLayout()
    ult.setContentsMargins(0, 0, 0, 0)

    # Button row
    button_row = QHBoxLayout()
    button_row.setSpacing(0)
    button_row.setContentsMargins(0, 0, 0, 0)
    
    btn_edit = QPushButton("Edit")
    btn_edit.clicked.connect(lambda: _make_editor(parent_window, "exe", load_data_func,
                                                   save_data_func, get_struc_func,
                                                   refresh_tab_func, pick_path_func,
                                                   web_profile))
    btn_edit.setFixedWidth(100)
    button_row.addWidget(btn_edit)
    
    btn_refresh = QPushButton("Refresh")
    btn_refresh.setFixedWidth(100)
    button_row.addWidget(btn_refresh)
    btn_refresh.clicked.connect(
        lambda: refresh_tab_func(parent_window.tabs, 2,
                                create_data_view(parent_window, load_data_func,
                                               save_data_func, get_struc_func,
                                               refresh_tab_func, pick_path_func,
                                               web_profile, "exe"))
    )
    
    button_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
    ult.addLayout(button_row)

    # Grid layout
    layout = QGridLayout()
    layout.setSpacing(50)
    layout.setContentsMargins(10, 10, 10, 30)
    ult.addLayout(layout)

    # Headings
    bold_font = QFont()
    bold_font.setBold(True)
    
    for i, heading in enumerate(EXE_HEADINGS):
        label = QLabel(heading)
        label.setFont(bold_font)
        label.setFixedHeight(30)
        layout.addWidget(label, 0, i)

    # Build data table
    build_data_table(EXE_KEYS, layout, (items[0],), "show", None)  # pyright: ignore[reportArgumentType]
    
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


def _make_editor(parent_window, editor_type, load_data_func, save_data_func,
                get_struc_func, refresh_tab_func, pick_path_func, web_profile):
    """Create and show an editor window."""
    from ui.editor_window import Editor
    parent_window.editor = Editor(
        editor_type, parent_window, load_data_func, save_data_func,
        get_struc_func, refresh_tab_func, pick_path_func, web_profile
    )
    parent_window.editor.show()