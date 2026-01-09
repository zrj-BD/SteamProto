"""
Main entry point for Steam Proto application.
"""
import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication

# Import modules
import web
import scanner
from theme_manager import get_theme_manager
from core.data_manager import load_data, save_data, create_blank, get_struc
from core.scan_scheduler import should_run_scan, execute_scan
from utils.constants import (
    METADATA_DEFAULT, RECENTS_FILE_DEFAULT, UI_FILE_DEFAULT,
    SETTINGS_FILE_DEFAULT, STATE_FILE_DEFAULT
)
from utils.helpers import refresh_tab, pick_path
from ui.main_window import MainWindow


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", "-m", default=METADATA_DEFAULT, 
                       help="Path to metadata JSON")
    parser.add_argument("--recentdata", "-r", default=RECENTS_FILE_DEFAULT, 
                       help="Path to recents JSON")
    parser.add_argument("--uidata", "-ui", default=UI_FILE_DEFAULT, 
                       help="Path to UI JSON")
    parser.add_argument("--settingsdata", "-settings", default=SETTINGS_FILE_DEFAULT, 
                       help="Path to settings JSON")
    parser.add_argument("--statedata", "-state", default=STATE_FILE_DEFAULT, 
                       help="Path to State JSON")
    return parser.parse_args()


def ensure_data_files_exist(args):
    """Ensure all required data files exist."""
    # Create metadata if it doesn't exist
    if not os.path.exists(args.metadata):
        scanner.main()
        web.main()
    
    # Create other files if they don't exist
    if not os.path.exists(args.uidata):
        create_blank(args.uidata)
    if not os.path.exists(args.settingsdata):
        create_blank(args.settingsdata)
    if not os.path.exists(args.statedata):
        create_blank(args.statedata)


def handle_automatic_scans(args):
    """Handle automatic scanning based on settings."""
    settings_data = load_data(["settings"], args)[0]
    state_data = load_data(["state"], args)[0]
    
    if should_run_scan(settings_data, state_data):
        execute_scan(
            web, 
            state_data, 
            lambda og, data, file: save_data(og, data, file, args)
        )


def main():
    """Main application entry point."""
    # Parse arguments
    global args
    args = parse_arguments()
    
    # Ensure data files exist
    ensure_data_files_exist(args)
    
    # Handle automatic scans
    handle_automatic_scans(args)
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Get theme manager
    theme_manager = get_theme_manager()
    
    # Create wrapper functions that include args
    def load_data_wrapper(files):
        return load_data(files, args)
    
    def save_data_wrapper(og, data, file, type="merge"):
        return save_data(og, data, file, args, type)
    
    def get_struc_wrapper(keys, layout, ref):
        return get_struc(keys, layout, ref)
    
    # Create main window
    window = MainWindow(
        load_data_func=load_data_wrapper,
        save_data_func=save_data_wrapper,
        get_struc_func=get_struc_wrapper,
        theme_manager=theme_manager,
        refresh_tab_func=refresh_tab,
        pick_path_func=pick_path,
    )
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()