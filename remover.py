"""
Marker Remover
Removes placed markers from game folders by main.py
Used in Rescanning
"""
import os
import argparse
from typing import List


def find_markers(base: str, marker_name: str):
    found: List[str]
    found = []
    for root, _, files in os.walk(base):
        for fn in files:
            if fn == marker_name:
                found.append(os.path.join(root, fn))
    return found


def remove_files(paths: List[str]) -> int:
    removed = 0
    for p in paths:
        try:
            os.remove(p)
            removed += 1
        except Exception:
            # skip deletion errors
            continue
    return removed


def main():
    p = argparse.ArgumentParser(description="Remove marker files (default: .processed_marker.txt) recursively.")
    p.add_argument("-d", "--dir", help="Base directory (default: current working directory)", default=os.path.dirname(os.getcwd()))
    p.add_argument("-m", "--marker", help="Marker filename to remove", default=".processed_marker.txt")
    args = p.parse_args()

    base = os.path.abspath(args.dir)
    markers = find_markers(base, args.marker)
    if not markers:
        print("No marker files found.")
        return

    print(f"Found {len(markers)} marker file(s).")
    for fp in markers:
        print("  " + fp)

    removed = remove_files(markers)
    print(f"Removed {removed} file(s).")


if __name__ == "__main__":
    main()