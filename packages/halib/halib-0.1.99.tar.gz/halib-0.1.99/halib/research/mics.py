from ..common import *
from ..filetype import csvfile
import pandas as pd
import platform


PC_NAME_TO_ABBR = {
    "DESKTOP-JQD9K01": "MainPC",
    "DESKTOP-5IRHU87": "MSI_Laptop",
    "DESKTOP-96HQCNO": "4090_SV",
    "DESKTOP-Q2IKLC0": "4GPU_SV",
    "DESKTOP-QNS3DNF": "1GPU_SV"
}

DEFAULT_ABBR_WORKING_DISK = {
    "MainPC": "E:",
    "MSI_Laptop": "D:",
    "4090_SV": "E:",
    "4GPU_SV": "D:",
}

def list_PCs(show=True):
    df = pd.DataFrame(list(PC_NAME_TO_ABBR.items()), columns=["PC Name", "Abbreviation"])
    if show:
        csvfile.fn_display_df(df)
    return df

def get_PC_name():
    return platform.node()

def get_PC_abbr_name():
    pc_name = get_PC_name()
    return PC_NAME_TO_ABBR.get(pc_name, "Unknown")

# ! This funcction search for full paths in the obj and normalize them according to the current platform and working disk
# ! E.g: "E:/zdataset/DFire", but working_disk: "D:", current_platform: "windows" => "D:/zdataset/DFire"
# ! E.g: "E:/zdataset/DFire", but working_disk: "D:", current_platform: "linux" => "/mnt/d/zdataset/DFire"
def normalize_paths(obj, working_disk, current_platform):
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = normalize_paths(value, working_disk, current_platform)
        return obj
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = normalize_paths(item, working_disk, current_platform)
        return obj
    elif isinstance(obj, str):
        # Normalize backslashes to forward slashes for consistency
        obj = obj.replace("\\", "/")
        # Regex for Windows-style path: e.g., "E:/zdataset/DFire"
        win_match = re.match(r"^([A-Z]):/(.*)$", obj)
        # Regex for Linux-style path: e.g., "/mnt/e/zdataset/DFire"
        lin_match = re.match(r"^/mnt/([a-z])/(.*)$", obj)
        if win_match or lin_match:
            rest = win_match.group(2) if win_match else lin_match.group(2)
            if current_platform == "windows":
                # working_disk is like "D:", so "D:/" + rest
                new_path = working_disk + "/" + rest
            elif current_platform == "linux":
                # Extract drive letter from working_disk (e.g., "D:" -> "d")
                drive_letter = working_disk[0].lower()
                new_path = "/mnt/" + drive_letter + "/" + rest
            else:
                # Unknown platform, return original
                return obj
            return new_path
    # For non-strings or non-path strings, return as is
    return obj
