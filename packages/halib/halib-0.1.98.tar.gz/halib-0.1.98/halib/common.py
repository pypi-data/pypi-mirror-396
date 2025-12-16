import os
import re
import rich
import arrow
import pathlib
from pathlib import Path
import urllib.parse

from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.pretty import pprint, Pretty
from pathlib import PureWindowsPath


console = Console()

def seed_everything(seed=42):
    import random
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    # import torch if it is available
    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except ImportError:
        pprint("torch not imported, skipping torch seed_everything")
        pass


def now_str(sep_date_time="."):
    assert sep_date_time in [
        ".",
        "_",
        "-",
    ], "sep_date_time must be one of '.', '_', or '-'"
    now_string = arrow.now().format(f"YYYYMMDD{sep_date_time}HHmmss")
    return now_string


def norm_str(in_str):
    # Replace one or more whitespace characters with a single underscore
    norm_string = re.sub(r"\s+", "_", in_str)
    # Remove leading and trailing spaces
    norm_string = norm_string.strip()
    return norm_string


def pprint_box(obj, title="", border_style="green"):
    """
    Pretty print an object in a box.
    """
    rich.print(
        Panel(Pretty(obj, expand_all=True), title=title, border_style=border_style)
    )

def console_rule(msg, do_norm_msg=True, is_end_tag=False):
    msg = norm_str(msg) if do_norm_msg else msg
    if is_end_tag:
        console.rule(f"</{msg}>")
    else:
        console.rule(f"<{msg}>")


def console_log(func):
    def wrapper(*args, **kwargs):
        console_rule(func.__name__)
        result = func(*args, **kwargs)
        console_rule(func.__name__, is_end_tag=True)
        return result

    return wrapper


class ConsoleLog:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        console_rule(self.message)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        console_rule(self.message, is_end_tag=True)
        if exc_type is not None:
            print(f"An exception of type {exc_type} occurred.")
            print(f"Exception message: {exc_value}")


def linux_to_wins_path(path: str) -> str:
    """
    Convert a Linux-style WSL path (/mnt/c/... or /mnt/d/...) to a Windows-style path (C:\...).
    """
    # Handle only /mnt/<drive>/... style
    if (
        path.startswith("/mnt/")
        and len(path) > 6
        and path[5].isalpha()
        and path[6] == "/"
    ):
        drive = path[5].upper()  # Extract drive letter
        win_path = f"{drive}:{path[6:]}"  # Replace "/mnt/c/" with "C:/"
    else:
        win_path = path  # Return unchanged if not a WSL-style path
    # Normalize to Windows-style backslashes
    return str(PureWindowsPath(win_path))


def pprint_local_path(
    local_path: str, get_wins_path: bool = False, tag: str = ""
) -> str:
    """
    Pretty-print a local path with emoji and clickable file:// URI.

    Args:
        local_path: Path to file or directory (Linux or Windows style).
        get_wins_path: If True on Linux, convert WSL-style path to Windows style before printing.
        tag: Optional console log tag.

    Returns:
        The file URI string.
    """
    p = Path(local_path).resolve()
    type_str = "📄" if p.is_file() else "📁" if p.is_dir() else "❓"

    if get_wins_path and os.name == "posix":
        # Try WSL → Windows conversion
        converted = linux_to_wins_path(str(p))
        if converted != str(p):  # Conversion happened
            file_uri = str(PureWindowsPath(converted).as_uri())
        else:
            file_uri = p.as_uri()
    else:
        file_uri = p.as_uri()

    content_str = f"{type_str} [link={file_uri}]{file_uri}[/link]"

    if tag:
        with ConsoleLog(tag):
            console.print(content_str)
    else:
        console.print(content_str)

    return file_uri
