"""
Reusable data table component for displaying game data.
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from PyQt6.QtWidgets import QGridLayout, QLabel, QLineEdit, QPushButton, QWidget, QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from utils.helpers import pick_path

def build_data_table(
    keys: Tuple[List[str], List[str]], 
    layout: QGridLayout, 
    files: Tuple[Dict[str, Dict[str, Any]], Optional[Dict[str, Dict[str, Any]]]], 
    mode: str, 
    window: Optional[QWidget],
):
    """
    Build a data table in a grid layout.
    
    Args:
        keys: Tuple of key lists for columns
        layout: Grid layout to populate
        files: Tuple of data dictionaries
        mode: "edit" or "show"
        window: Parent window widget
    """


    n = 1
    for i in files[0]:
        label = QLabel(i)
        layout.addWidget(label, n, 0)

        if mode == "edit":
            _keys = [keys[0]]
        elif mode == "show":
            _keys = keys
        else:
            _keys = []
        
        para = 0
        for j in _keys:
            if para == 0:
                p = 1 
            else:
                p = len(_keys[0]) + 1
                
            for k in j:
                if k == "date":
                    try:
                        date_obj = datetime.fromtimestamp(files[para][i]["date"])  # pyright: ignore[reportOptionalSubscript]
                    except Exception:
                        date_obj = None
                    label = QLabel(str(date_obj))
                    
                elif k == "exesrc":
                    if mode == "show":
                        try:
                            label = QLabel(files[para][i][k])  # pyright: ignore[reportOptionalSubscript]
                        except Exception:
                            label = QLabel("")
                    elif mode == "edit":
                        try: 
                            label = QPushButton(files[para][i][k])  # pyright: ignore[reportOptionalSubscript]
                        except Exception:
                            label = QPushButton(None)
                        label.clicked.connect(lambda checked, folder=i, l=label, w=window: l.setText(pick_path(w, folder))) # type: ignore
                            
                elif k == "png":
                    from ui.components.pixmaps import CHECK_PIX, X_PIX
                    if mode == "show":
                        label = QLabel()
                        pix = CHECK_PIX if os.path.exists(f"data/imgs/{i}.png") else X_PIX
                        label.setPixmap(pix)
                        
                    if mode == "edit":
                        label = QWidget()
                        label_layout = QHBoxLayout()
                        label_layout.setContentsMargins(0, 0, 0, 0)
                        pix = CHECK_PIX if os.path.exists(f"data/imgs/{i}.png") else X_PIX
                        image = QLabel()
                        image.setPixmap(pix)
                        button = QPushButton("Change/Add")
                        try:
                            button.clicked.connect(lambda checked, game=i, w=window: w.pick_img_view(game))  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                        except Exception:
                            pass
                        label_layout.addWidget(image)
                        label_layout.addWidget(button)                  
                        label.setLayout(label_layout)
                        
                else:
                    if mode == "show":
                        try:
                            label = QLabel(files[para][i][k])  # pyright: ignore[reportOptionalSubscript]
                        except Exception:
                            label = QLabel("")
                    elif mode == "edit":
                        try:
                            label = QLineEdit(files[para][i][k])  # pyright: ignore[reportOptionalSubscript]
                        except Exception:
                            label = QLineEdit("")
                        label.setMaximumWidth(200)
                        
                label.setFixedHeight(40)
                layout.addWidget(label, n, p)
                p += 1
                
            para += 1
            if len(files) == 2 and mode == "show":
                from ui.components.pixmaps import CHECK_PIX, X_PIX
                status = QLabel()
                length = len(_keys[0]) + len(_keys[1]) + 1
                try:
                    pix = CHECK_PIX if files[0][i]["build"] == files[1][i]["build"] else X_PIX  # pyright: ignore[reportOptionalSubscript]
                    status.setPixmap(pix)
                except Exception:
                    pass
                layout.addWidget(status, n, length)

        n += 1