import os
import json
import argparse
import re
import subprocess
from typing import Dict, Any, List

METADATA_DEFAULT = os.path.join(os.path.dirname(os.getcwd()), "_metadata", "metadata.json")
OUT_FILE_DEFAULT = os.path.join(os.path.dirname(os.getcwd()), "_metadata", "recents.json")
STEAMCMD_PATH = "C:\\steamcmd\\steamcmd.exe"

def load_metadata(path: str) -> Dict[str, Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def get_latest_build_info(appids: List[str]) -> Dict[str, Dict[str, Any]]:
    cmd = [STEAMCMD_PATH, "+login", "anonymous"]
    for appid in appids:
        cmd += ["+app_info_print", str(appid)]
    cmd += ["+quit"]

    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, encoding="utf-8")

    results: Dict[str, Dict[str, Any]] = {}

    # Split output by "AppID : <appid>"
    app_blocks = re.split(r'AppID\s*:\s*(\d+)', output)
    # re.split produces [preamble, appid1, block1, appid2, block2, ...]

    for i in range(1, len(app_blocks), 2):
        appid = app_blocks[i]
        text = app_blocks[i + 1]

        public_branch = re.search(r'"branches"\s*\{.*?"public"\s*\{(.*?)\n\s*\}', text, re.DOTALL)
        if not public_branch:
            results[appid] = {"appid": appid, "build": None, "time": None}
            continue

        section = public_branch.group(1)
        build_match = re.search(r'"buildid"\s+"(\d+)"', section)
        time_match = re.search(r'"timeupdated"\s+"(\d+)"', section)

        results[appid] = {
            "appid": appid,
            "build": build_match.group(1) if build_match else None,
            "date": int(time_match.group(1)) if time_match else None,
        }

    return results

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", "-m", default=METADATA_DEFAULT)
    p.add_argument("--out", "-o", default=OUT_FILE_DEFAULT)
    args = p.parse_args()

    meta = load_metadata(args.metadata)
    game_to_appid = {name: str(info["appid"]) for name, info in meta.items() if info.get("appid")}

    steam_data = get_latest_build_info(list(game_to_appid.values()))

    results: Dict[str, Dict[str, Any]] = {}
    for game, appid in game_to_appid.items():
        if appid in steam_data:
            results[game] = steam_data[appid]
        else:
            results[game] = {"appid": appid, "build": None, "date": None}

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()