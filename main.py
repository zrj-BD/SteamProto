import os
import json
import argparse
import re
from typing import Dict, List, Any, Optional, Set, Tuple, DefaultDict
from collections import defaultdict
import time 
# crazy bro. you removed that and got yourself like 1h on top. but youre actually getting how it works kinda now. you understood yourself
# Simple, explicit mappings (defaults).
DEFAULT_SEARCHABLE_EXTS = [".txt", ".ini"]

DEFAULT_CONTENT_MAPPINGS = [
    # {"key": "version", "keywords": ["version", "ver", "build"], "extract_regex": r"(\d+(?:\.\d+)+|\d+)"},
    {"key": "appid", "keywords": ["appid", "app id"], "extract_regex": r"(\d{6,})"},
    # {"key": "updated_to", "keywords": ["updated to", "updated"], "extract_regex": r"(\d+(?:\.\d+)+|\d+)"},
    {"key": "emulator", "keywords": ["rexa"], "value": "REXA"},
    {"key": "emulator", "keywords": ["rune"], "value": "RUNE"},
    {"key": "emulator", "keywords": ["gse"], "value": "Goldberg"},
    {"key": "emulator", "keywords": ["goldberg"], "value": "Goldberg"},
    {"key": "build", "keywords": ["build"], "extract_regex": r"(\d{7,})"},
]

# Filename mappings: match filename stem to decide which files to inspect;
# if extract_regex present, the value is read from the content of matched files (not from the filename).
DEFAULT_FILENAME_MAPPINGS = [
    {"key": "appid", "keywords": ["appid"], "extract_regex": r"(\d{6,})"},
    {"key": "version", "keywords": ["version"], "extract_regex": r"(\d+(?:\.\d+)+)"}, # |\d+
    {"key": "build", "keywords": ["build"], "extract_regex": r"(\d{7,})"},
]

DEFAULT_EXTENSION_MAPPINGS = [
    {"extensions": [".rne"], "key": "emulator", "value": "RUNE"},
    {"extensions": [".rexa"], "key": "emulator", "value": "REXA"},
]


def normalize_path(p: str) -> str:
    return os.path.normpath(os.path.abspath(p))


def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            cfg = json.load(fh)
            return cfg if isinstance(cfg, dict) else {}
    except Exception:
        return {}


def _match_value_from_regex(m: Optional[re.Match]) -> Optional[str]:
    """Safely extract first capturing group if present else full match. Avoid IndexError."""
    if not m:
        return None
    # prefer first capture group if any exist
    try:
        if m.lastindex and m.lastindex >= 1:
            return m.group(1)
    except Exception:
        pass
    try:
        return m.group(0)
    except Exception:
        return None


def compile_mappings(cfg: Dict[str, Any]):
    content = cfg.get("content_mappings") or cfg.get("DEFAULT_CONTENT_MAPPINGS") or DEFAULT_CONTENT_MAPPINGS
    filename = cfg.get("filename_mappings") or cfg.get("DEFAULT_FILENAME_MAPPINGS") or DEFAULT_FILENAME_MAPPINGS
    extension = cfg.get("extension_mappings") or cfg.get("DEFAULT_EXTENSION_MAPPINGS") or DEFAULT_EXTENSION_MAPPINGS
    searchable_exts = cfg.get("searchable_exts") or DEFAULT_SEARCHABLE_EXTS

    for lst in (content, filename):
        for entry in lst:
            entry["keywords"] = [k.lower() for k in entry.get("keywords", [])]
            entry["key"] = str(entry["key"])
            if "extract_regex" in entry and entry["extract_regex"]:
                # ensure capture groups exist in filename mappings where expected
                entry["_extract_re"] = re.compile(entry["extract_regex"], flags=re.IGNORECASE)

    for entry in extension:
        entry["extensions"] = [e.lower() for e in entry.get("extensions", [])] #_ensure_dot()
        entry["key"] = str(entry["key"])

    searchable_exts = [e.lower() for e in searchable_exts] #_ensure_dot()
    return content, filename, extension, searchable_exts


def load_existing_metadatas(meta_dir: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load both metadata.json and metadata_fix.json if present, return two dicts.
    If not present return empty dicts. Sanitize bad keys.
    """
    meta1_path = os.path.join(meta_dir, "metadata.json")
    meta2_path = os.path.join(meta_dir, "metadata_fix.json")
    meta1 = {}
    meta2 = {}
    if os.path.exists(meta1_path):
        try:
            with open(meta1_path, "r", encoding="utf-8") as fh:
                meta1 = json.load(fh) or {}
        except Exception:
            meta1 = {}
    if os.path.exists(meta2_path):
        try:
            with open(meta2_path, "r", encoding="utf-8") as fh:
                meta2 = json.load(fh) or {}
        except Exception:
            meta2 = {}

    return meta1, meta2


def merge_value(existing, new):
    if existing == new:
        return existing
    if isinstance(existing, list):
        if new not in existing:
            existing.append(new)
        return existing
    else:
        if existing != new:
            return [existing, new]
        return existing


def save_metadata_outputs(meta_dir: str, meta1: Dict[str, Any], meta2: Dict[str, Any]):
    os.makedirs(meta_dir, exist_ok=True)
    path1 = os.path.join(meta_dir, "metadata.json")
    path2 = os.path.join(meta_dir, "metadata_fix.json")
    with open(path1, "w", encoding="utf-8") as fh:
        json.dump(meta1, fh, indent=2, ensure_ascii=True)
    with open(path2, "w", encoding="utf-8") as fh:
        json.dump(meta2, fh, indent=2, ensure_ascii=True)


def collect_roots(base: str, skip_dirs: Optional[Set[str]] = None) -> DefaultDict[str, List[Tuple[str, List[str]]]]:
    """
    Walk base and group roots/files per immediate child folder (top_key).
    Returns mapping: top_key -> list of (root_path, files_in_root)
    Skips any directory names in skip_dirs.
    NOTE: do not create a special "_root" key for files directly in base (we skip rel==".")
    """
    if skip_dirs is None:
        skip_dirs = {"_metadata"}
    groups: DefaultDict[str, List[Tuple[str, List[str]]]] = defaultdict(list)
    for root, dirs, files in os.walk(base):
        # prevent descending into metadata output folder
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        rel = os.path.relpath(root, base)
        # skip the base root itself (avoid creating a "_root" top key)
        if rel == ".":
            continue
        top_key = rel.split(os.sep)[0]
        groups[top_key].append((root, files))
    return groups


def analyze_group(roots: List[Tuple[str, List[str]]],
                  content_maps: List[Dict[str, Any]],
                  filename_maps: List[Dict[str, Any]],
                  extension_maps: List[Dict[str, Any]],
                  searchable_exts: List[str]) -> Dict[str, Any]:
    """
    Analyze all roots belonging to a single top folder and return metadata dict for that top folder.
    """
    folder_meta: Dict[str, Any] = {}

    def set_meta(k: str, v: Any):
        if k in folder_meta:
            folder_meta[k] = merge_value(folder_meta[k], v)
        else:
            folder_meta[k] = v

    # helper: find earliest occurrence of any keyword in content (return keyword and index) or (None, -1)
    def find_earliest_keyword(content_lower: str, keywords: List[str]) -> Tuple[Optional[str], int]:
        best_kw = None
        best_idx = -1
        for kw in keywords:
            idx = content_lower.find(kw)
            if idx != -1 and (best_idx == -1 or idx < best_idx):
                best_kw = kw
                best_idx = idx
        return best_kw, best_idx

    # 1) Content mappings
    for root, files in roots:
        for fn in files:
            _, ext = os.path.splitext(fn)
            if ext.lower() not in searchable_exts:
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
            except Exception:
                continue
            content_l = content.lower()
            for cm in content_maps:
                if cm["key"] in folder_meta:
                    continue

                # find earliest occurrence among all keywords in this file (so mapping respects file order)
                found_kw, found_idx = find_earliest_keyword(content_l, cm.get("keywords", []))
                if not found_kw:
                    continue

                # if mapping defines fixed value, set and stop searching this mapping
                if "value" in cm:
                    set_meta(cm["key"], cm["value"])
                    continue

                val = None
                # If an extract regex exists: only accept matches from that regex.
                if "_extract_re" in cm:
                    # check every occurrence of the keyword (in file order) and try regex on the tail after that occurrence
                    for m_kw in re.finditer(re.escape(found_kw), content_l):
                        tail_pos = m_kw.end()
                        tail_all = content[tail_pos:]
                        m = cm["_extract_re"].search(tail_all)
                        val = _match_value_from_regex(m)
                        if val is not None:
                            break

                if val is not None:
                    set_meta(cm["key"], val)
                # once a mapping is set we skip it in later files/lines (handled by top-of-loop check)

    # 2) Filename mappings: match stem, then read content of matched files and extract (not value from filename)
    for fm in filename_maps:
        if fm["key"] in folder_meta:
            continue
        for root, files in roots:
            for fn in files:
                stem = os.path.splitext(fn)[0].lower()
                if any(kw in stem for kw in fm["keywords"]):
                    if "value" in fm:
                        set_meta(fm["key"], fm["value"])
                        break
                    if "_extract_re" in fm:
                        path = os.path.join(root, fn)
                        try:
                            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                                content = fh.read()
                        except Exception:
                            continue
                        content_l = content.lower()

                        # find earliest keyword occurrence(s), and try regex after each occurrence
                        found_kw, _ = find_earliest_keyword(content_l, fm.get("keywords", []))
                        val = None
                        if found_kw:
                            for m_kw in re.finditer(re.escape(found_kw), content_l):
                                tail_pos = m_kw.end()
                                tail_all = content[tail_pos:]
                                m = fm["_extract_re"].search(tail_all)
                                val = _match_value_from_regex(m)
                                if val is not None:
                                    break
                        # fallback: regex on whole content (allowed for filename mappings)
                        if val is None:
                            m2 = fm["_extract_re"].search(content)
                            val = _match_value_from_regex(m2)
                        if val is not None:
                            set_meta(fm["key"], val)
                            break
            if fm["key"] in folder_meta:
                break

    # 3) Extension presence mapping
    for em in extension_maps:
        for root, files in roots:
            names_lower = [f.lower() for f in files]
            for ext in em["extensions"]:
                if any(n.endswith(ext) for n in names_lower):
                    set_meta(em["key"], em["value"])
                    break
            if em["key"] in folder_meta:
                break

    return folder_meta


def mark_top_folder(base: str, top_key: str, marker_name: str, marker_code: str):
    """
    Create marker file inside the real top-level folder to indicate processed.
    """
    if top_key == "_root":
        target = base
    else:
        target = os.path.join(base, top_key)
    try:
        os.makedirs(target, exist_ok=True)
        with open(os.path.join(target, marker_name), "w", encoding="utf-8") as fh:
            fh.write(marker_code)
    except Exception:
        pass


def top_folder_is_marked(base: str, top_key: str, marker_name: str) -> bool:
    if top_key == "_root":
        path = os.path.join(base, marker_name)
    else:
        path = os.path.join(base, top_key, marker_name)
    return os.path.exists(path)


def main():
    parser = argparse.ArgumentParser(description="Scan folders, extract folder-level metadata and write two JSONs.")
    parser.add_argument("-d", "--dir", required=False, help="Base directory to scan (default: parent dir)")
    parser.add_argument("-c", "--config", help="Optional JSON config to override mappings")
    parser.add_argument("-o", "--out", help="Output folder for metadata (default: _metadata/)")
    parser.add_argument("--force", action="store_true", help="Rescan all folders (ignore markers)")
    parser.add_argument("--marker-name", default=".processed_marker.txt", help="Marker filename placed in processed folders")
    parser.add_argument("--marker-code", default="###99999###", help="Content written into marker file")
    args = parser.parse_args()

    base = normalize_path(args.dir) if args.dir else normalize_path(os.path.dirname(os.getcwd()))
    cfg = load_config(args.config) if args.config else {}
    content_maps, filename_maps, extension_maps, searchable_exts = compile_mappings(cfg)

    meta_dir = args.out if args.out else os.path.abspath("_metadata")
    program_dir = normalize_path(os.path.dirname(__file__))
    existing_meta1, existing_meta2 = load_existing_metadatas(meta_dir)

    # collect groups under base, skip metadata folder so we don't descend into it
    groups = collect_roots(base, skip_dirs={os.path.basename(meta_dir)})

    to_process: List[str] = []
    for top_key in groups.keys():
        # skip metadata output itself
        if top_key == os.path.basename(meta_dir) or top_key == os.path.basename(program_dir):
            continue
        # skip already marked folders (unless force)
        if not args.force and top_folder_is_marked(base, top_key, args.marker_name):
            continue
        to_process.append(top_key)

    for tk in to_process:
        roots = groups.get(tk, [])
        meta = analyze_group(roots, content_maps, filename_maps, extension_maps, searchable_exts)
        meta["date"] = int(time.time())
        # ensure an entry exists so it is tracked; append to both metadata files
        existing_meta1[tk] = meta
        existing_meta2[tk] = meta.copy() if isinstance(meta, dict) else meta
        # mark folder as processed
        mark_top_folder(base, tk, args.marker_name, args.marker_code)

    # save both files separately (they may be identical)
    save_metadata_outputs(meta_dir, existing_meta1, existing_meta2)

    print(f"Processed {len(to_process)} new folders. Total entries now: {len(existing_meta1)}")
    print(f"Metadata written to {meta_dir}/metadata.json and {meta_dir}/metadata_fix.json")


if __name__ == "__main__":
    main()