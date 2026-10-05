import os
from pathlib import Path

# JARVIS may only touch files inside these folders
ROOTS = [Path.home(), Path(r"C:\JARVIS")]

MAX_CHARS = 8000
MAX_ITEMS = 100
MAX_RESULTS = 50
MAX_SCANNED = 30000
SKIP_DIRS = {"appdata", "node_modules", "__pycache__", "$recycle.bin", "windows", "program files"}
TEXT_SUFFIXES = {
    ".txt", ".md", ".py", ".json", ".csv", ".log", ".ini", ".toml", ".yaml", ".yml",
    ".c", ".h", ".cpp", ".hpp", ".java", ".js", ".html", ".css", ".xml", ".tex", ".bat", ".ps1",
}


def _resolve(path):
    """Turn a user path into a safe absolute path, or raise ValueError."""
    p = Path(path.strip() or ".").expanduser()
    if not p.is_absolute():
        p = Path.home() / p
    p = p.resolve()
    for root in ROOTS:
        root = root.resolve()
        if p == root or root in p.parents:
            return p
    raise ValueError(f"Access denied: {p} is outside the allowed folders.")


def list_folder(path: str = "") -> str:
    """List the files and subfolders inside a folder on the user's PC.

    Args:
        path: Folder path. Relative paths like 'Documents' or 'Desktop' are
            relative to the user's home folder. Empty string means the home folder.
    """
    try:
        folder = _resolve(path)
        if not folder.is_dir():
            return f"Not a folder: {folder}"
        entries = sorted(folder.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        lines = []
        for e in entries[:MAX_ITEMS]:
            if e.is_dir():
                lines.append(f"[DIR]  {e.name}")
            else:
                try:
                    size_kb = e.stat().st_size / 1024
                    lines.append(f"[FILE] {e.name} ({size_kb:.1f} KB)")
                except OSError:
                    lines.append(f"[FILE] {e.name}")
        extra = len(entries) - MAX_ITEMS
        if extra > 0:
            lines.append(f"... and {extra} more items")
        return f"Contents of {folder}:\n" + ("\n".join(lines) if lines else "(empty)")
    except (ValueError, OSError) as e:
        return f"Error: {e}"


def read_text_file(path: str) -> str:
    """Read the text content of a file on the user's PC (txt, md, py, c, json, csv, ...).

    Args:
        path: File path. Relative paths are relative to the user's home folder.
    """
    try:
        f = _resolve(path)
        if not f.is_file():
            return f"Not a file: {f}"
        if f.suffix.lower() not in TEXT_SUFFIXES:
            return f"Won't read {f.suffix or 'this'} files, only plain text types."
        text = f.read_text(encoding="utf-8", errors="replace")
        if len(text) > MAX_CHARS:
            return text[:MAX_CHARS] + f"\n... [truncated, file has {len(text)} characters]"
        return text or "(file is empty)"
    except (ValueError, OSError) as e:
        return f"Error: {e}"


def search_files(name_contains: str, folder: str = "") -> str:
    """Search for files whose name contains some text, inside a folder and its subfolders.

    Args:
        name_contains: Text to look for in file names (case-insensitive).
        folder: Where to search. Relative paths are relative to the user's home folder.
            Empty string means the home folder.
    """
    try:
        start = _resolve(folder)
        if not start.is_dir():
            return f"Not a folder: {start}"
        needle = name_contains.lower()
        found, scanned = [], 0
        for dirpath, dirnames, filenames in os.walk(start):
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and d.lower() not in SKIP_DIRS
            ]
            for name in filenames:
                scanned += 1
                if needle in name.lower():
                    found.append(os.path.join(dirpath, name))
                    if len(found) >= MAX_RESULTS:
                        return "Matches (stopped at limit):\n" + "\n".join(found)
            if scanned >= MAX_SCANNED:
                break
        if not found:
            return f"No files with '{name_contains}' in the name (scanned {scanned} files)."
        return "Matches:\n" + "\n".join(found)
    except (ValueError, OSError) as e:
        return f"Error: {e}"