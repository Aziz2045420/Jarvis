import subprocess
from pathlib import Path

import safety

WORKSPACE = Path(__file__).with_name("workspace")
ALLOWED_SUFFIXES = {".txt", ".md", ".py", ".json", ".csv"}
MAX_CHARS = 20000

# Only these apps can be opened. Add more as "name": "program.exe".
APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe",
}


def open_app(name: str) -> str:
    """Open an application on the user's PC. The user is asked to confirm first.

    Args:
        name: App name. Available: notepad, calculator, paint, file explorer.
    """
    key = name.strip().lower()
    exe = APPS.get(key)
    if not exe:
        return f"I can't open '{name}'. Available apps: {', '.join(sorted(APPS))}."
    if not safety.confirm(f"JARVIS wants to open {key}."):
        return "The user declined. Do not retry."
    try:
        subprocess.Popen([exe])
    except OSError as e:
        return f"Couldn't open {key}: {e}"
    return f"Opened {key}."


def create_text_file(filename: str, content: str) -> str:
    """Create a NEW text file in the JARVIS workspace folder (C:/JARVIS/workspace).
    The user is asked to confirm first. Cannot overwrite existing files.

    Args:
        filename: File name like 'todo.txt'. Allowed types: txt, md, py, json, csv.
        content: The full text to write into the file.
    """
    WORKSPACE.mkdir(exist_ok=True)
    root = WORKSPACE.resolve()
    target = (root / filename.strip()).resolve()
    if root not in target.parents:
        return "Refused: files can only be created inside the workspace folder."
    if target.suffix.lower() not in ALLOWED_SUFFIXES:
        return f"Refused: only {', '.join(sorted(ALLOWED_SUFFIXES))} files are allowed."
    if target.exists():
        return f"{target.name} already exists. Choose another name."
    if len(content) > MAX_CHARS:
        return "Refused: content is too long."
    preview = content[:300] + ("..." if len(content) > 300 else "")
    question = f"JARVIS wants to create {target}\n--- preview ---\n{preview}\n---------------"
    if not safety.confirm(question):
        return "The user declined. Do not retry."
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except OSError as e:
        return f"Couldn't write the file: {e}"
    return f"Created {target}"