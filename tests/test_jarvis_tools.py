from pathlib import Path

import actions
import files


def test_search_text_in_files_finds_match(tmp_path, monkeypatch):
    target = tmp_path / "nested"
    target.mkdir()
    file_path = target / "notes.txt"
    file_path.write_text("hello world\nsecond line\n", encoding="utf-8")

    result = files.search_text_in_files("hello", str(target))

    assert "notes.txt" in result
    assert "hello" in result


def test_create_folder_creates_inside_workspace(monkeypatch, tmp_path):
    monkeypatch.setattr(actions.safety, "confirm", lambda question: True)
    base = tmp_path / "workspace"
    base.mkdir()
    monkeypatch.setattr(actions, "WORKSPACE", base)

    result = actions.create_folder("demo-folder")

    assert "Created" in result
    assert (base / "demo-folder").exists()
