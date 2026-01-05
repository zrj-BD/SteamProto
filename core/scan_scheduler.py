"""
Automatic scan scheduling logic.
"""
from datetime import datetime, date
from typing import Dict, Any


def should_run_scan(settings_data: Dict[str, Any], state_data: Dict[str, Any]) -> bool:
    """
    Determine if an automatic scan should run based on settings and state.
    
    Args:
        settings_data: Settings dictionary with automatic_scans and scan_frequency
        state_data: State dictionary with last_scan_date
        
    Returns:
        True if scan should run, False otherwise
    """
    if not settings_data.get("automatic_scans", False):
        return False
    
    scan_frequency = settings_data.get("scan_frequency", "weekly")
    today = date.today()
    today_str = str(today)
    
    last_scan_date_val = state_data.get("last_scan_date", "")
    last_scan_date_str = str(last_scan_date_val) if last_scan_date_val else ""
    has_not_scanned_today = last_scan_date_str != today_str
    
    if scan_frequency == "daily":
        return has_not_scanned_today
        
    elif scan_frequency == "weekly":
        return today.weekday() == 6 and has_not_scanned_today
            
    elif scan_frequency == "biweekly":
        if last_scan_date_str:
            try:
                last_scan_date = datetime.strptime(last_scan_date_str, "%Y-%m-%d").date()
                days_since_scan = (today - last_scan_date).days
                return days_since_scan >= 14
            except (ValueError, TypeError):
                return True
        else:
            return True
            
    elif scan_frequency == "monthly":
        return today.day == 1 and has_not_scanned_today
    
    return False


def execute_scan(web_module, state_data: Dict[str, Any], save_data_func):
    """
    Execute a scan and update the last scan date.
    
    Args:
        web_module: Module with main() function to execute scan
        state_data: State dictionary to update
        save_data_func: Function to save state data
    """
    web_module.main()
    today_str = str(date.today())
    save_data_func(state_data, {"last_scan_date": today_str}, "state")
    print(f"Automatic scan executed on {today_str}")