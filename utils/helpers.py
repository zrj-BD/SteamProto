"""
Utility helper functions.
"""
import os
import subprocess
from typing import Optional, Callable
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QTabWidget, QWidget, QMessageBox


def refresh_tab(tabs: QTabWidget, index: int, tab: QWidget):
    """
    Refresh a tab by removing and reinserting it.
    
    Args:
        tabs: QTabWidget containing the tabs
        index: Index of tab to refresh
        tab: New tab widget to insert
    """
    current = tabs.currentIndex()
    name = tabs.tabText(index)
    tabs.removeTab(index)
    tabs.insertTab(index, tab, name)
    if current == index:
        tabs.setCurrentIndex(index)


def confirm(parent: QWidget, message: str, action: Callable, default: str):
    """
    Show a confirmation dialog and execute action if confirmed.
    
    Args:
        parent: Parent widget
        message: Confirmation message
        action: Function to execute if confirmed
        default: Default button ("Yes" or "No")
    """
    msg_box = QMessageBox(parent)
    msg_box.resize(400, 200)
    msg_box.setWindowTitle("Confirm Action")
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(getattr(QMessageBox.StandardButton, default))
    
    result = msg_box.exec()
    if result == QMessageBox.StandardButton.Yes:
        action()


def pick_path(window: QWidget, folder: str, label):
    """
    Open a file dialog to pick an executable file.
    
    Args:
        window: Parent window
        folder: Default folder to open
        label: Label widget to update with selected path
    """
    path, _ = QFileDialog.getOpenFileName(
        window,
        "Select EXE",
        os.path.join(os.path.dirname(os.getcwd()), folder),
        "Executable Files (*.exe);;All Files (*)"
    )
    if path:
        label.setText(path)


def run_exe(exe: str, parent_window: Optional[QMainWindow] = None):
    """
    Run an executable file.
    
    Args:
        exe: Path to executable file
        parent_window: Optional parent window to close after launching
    """
    try: 
        subprocess.Popen([exe], cwd=os.path.dirname(exe))
        if parent_window:
            parent_window.close()
    except Exception as e:
        print(f"Error running exe: {e}")