"""
Utility helper functions.
"""
import os
import sys
import subprocess
from typing import Optional, Callable
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QTabWidget, QWidget, QMessageBox
from PyQt6.QtCore import QCoreApplication


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
    msg_box.setWindowTitle(QCoreApplication.translate("msg", "Confirm Action"))
    msg_box.setText(QCoreApplication.translate("msg", message))
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    btn_y = msg_box.button(QMessageBox.StandardButton.Yes)
    btn_n = msg_box.button(QMessageBox.StandardButton.No)
    btn_y.setText(QCoreApplication.translate("msg", "Yes")) # type: ignore
    btn_n.setText(QCoreApplication.translate("msg", "No")) # type: ignore
    msg_box.setDefaultButton(getattr(QMessageBox.StandardButton, default))
    
    result = msg_box.exec()
    if result == QMessageBox.StandardButton.Yes:
        action()


def pick_path(window: QWidget, folder: str, type="exe"):
    """
    Open a file or directory dialog based on type.
    """
    # Define start path
    start_path = os.path.join(os.path.dirname(os.getcwd()), folder)
    
    if type == "exe":
        title = QCoreApplication.translate("PathDialog", "Select EXE")
        file_filter = "Executable Files (*.exe);;All Files (*)"
        path, _ = QFileDialog.getOpenFileName(window, title, start_path, file_filter)
    
    elif type == "dir":
        title = QCoreApplication.translate("PathDialog", "Select Game Directory")
        # getExistingDirectory returns only the path string, not a tuple
        path = os.path.relpath(QFileDialog.getExistingDirectory(window, title, start_path), start_path)

    return path


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


def restart_script(script_path=None):
    """
    Restart a Python script.
    If script_path is None, restarts the current script.
    """
    python = os.path.abspath(sys.executable)
    if script_path is None:
        # Restart the currently running script
        script_path = os.path.abspath(sys.argv[0])
    else:
        script_path = os.path.abspath(script_path)
    subprocess.Popen([python, script_path] + sys.argv[1:], close_fds=True)
    sys.exit(0)