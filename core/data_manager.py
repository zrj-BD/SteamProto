"""
Data loading, saving, and validation logic.
"""
import json
import os
from typing import Dict, Any, List, Tuple, Optional


def load_data(files: List[str], args) -> Tuple[Dict[str, Any], ...]:
    """
    Load JSON files and return their contents as dictionaries.
    
    Args:
        files: List of file keys (e.g., ["meta", "recent"])
        args: Argument namespace with file paths
        
    Returns:
        Tuple of dictionaries, one for each file
    """
    result = []
    for file_key in files:
        data: Dict[str, Any] = {}
        path = getattr(args, f"{file_key}data")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except (json.JSONDecodeError, IOError, OSError):
                pass
        result.append(data)
    return tuple(result)


def save_data(og: Dict[str, Any], data: Dict[str, Any], file: str, args, type="merge"):
    """
    Merge and save data to JSON file.
    
    Args:
        og: Original data dictionary
        data: New data to merge
        file: File key (e.g., "meta", "settings")
        args: Argument namespace with file paths
        type: merge with old data ("merge") or not (etc.)
    """

    def merge(og: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries."""
        for key, value in data.items():
            if isinstance(value, dict) and key in og and isinstance(og[key], dict):
                merge(og[key], value)
            else:
                og[key] = value
        return og
    
    if type == "merge":
        write = merge(og, data)
    else: 
        write = data
    path = getattr(args, f"{file}data")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(write, fh, indent=2, ensure_ascii=True)


def ui_updater(save_data_func, meta, dict_ui):
    """
    Update UI data.
    
    Args:
        save_data_func: Function to save data
        meta: metadata game names reference
        dict_ui: current ui game names
    """
    write: Dict[str, Any] = dict_ui
    for i in meta:
        try: 
            dict_ui[i]
            pass
        except KeyError:
            write[i] = {}

    save_data_func(None, write, "ui", "no-merge")


def create_blank(loc: str):
    """
    Create a blank JSON file at the specified location.
    
    Args:
        loc: File path
    """
    with open(loc, "w", encoding="utf-8") as fh:
        json.dump({}, fh, indent=2, ensure_ascii=True)


def get_struc(keys: List[str], layout, ref: Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    """
    Extract structure data from layout widgets.
    
    Args:
        keys: List of keys to extract
        layout: Grid layout containing widgets
        ref: Tuple of (metadata dict, recent dict)
        
    Returns:
        Dictionary with extracted values
    """
    import time
    n = 1
    out = {}
    build = ""
    
    for i in ref[0]:
        out[i] = {}
        p = 1
        for k in keys:
            if k == "build":
                widget = layout.itemAtPosition(n, p)
                if widget is not None:
                    build = widget.widget().text()
            if k == "date":
                if build == "" or (ref[1].get(i, {}).get("build") and build == ref[1][i]["build"]):
                    out[i][k] = int(time.time())
                else:
                    out[i][k] = ref[0][i].get("date", int(time.time()))
            elif k == "png":
                continue
            else:
                widget = layout.itemAtPosition(n, p)
                if widget is not None:
                    text = widget.widget().text()
                    if text:
                        out[i][k] = text
            p += 1
        n += 1
    return out