import json
from datetime import date, datetime
from pathlib import Path

MEMORY_FILE = Path(__file__).with_name("jarvis_memory.json")
MAX_FACTS = 200


def _load():
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save(facts):
    MEMORY_FILE.write_text(
        json.dumps(facts, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def remember(fact: str) -> str:
    """Save a lasting fact about the user (name, preferences, projects, habits).

    Args:
        fact: One short sentence, e.g. 'The user studies computer science at THI'.
    """
    fact = fact.strip()
    if not fact:
        return "Nothing to remember."
    facts = _load()
    if any(f["fact"].lower() == fact.lower() for f in facts):
        return "Already remembered."
    if len(facts) >= MAX_FACTS:
        return "Memory is full. Ask the user to forget something first."
    facts.append({"fact": fact, "date": date.today().isoformat()})
    _save(facts)
    return f"Remembered: {fact}"


def list_memories() -> str:
    """List everything saved about the user, numbered."""
    facts = _load()
    if not facts:
        return "Nothing saved yet."
    return "\n".join(f"{i}. {f['fact']}" for i, f in enumerate(facts, 1))


def forget(number: int) -> str:
    """Delete one saved fact by its number from list_memories.

    Args:
        number: The 1-based number of the fact to delete.
    """
    facts = _load()
    if not 1 <= number <= len(facts):
        return f"No fact number {number}. There are {len(facts)} saved."
    removed = facts.pop(number - 1)
    _save(facts)
    return f"Forgot: {removed['fact']}"


def memory_prompt() -> str:
    """Text appended to the system prompt on every message:
    the current date/time plus everything saved about the user."""
    now = datetime.now().strftime("%A, %d %B %Y, %H:%M")
    text = (
        f"\n\nCurrent local date and time: {now}. "
        "Always trust this for the date and time, never guess it."
    )
    facts = _load()
    if facts:
        lines = "\n".join(f"- {f['fact']}" for f in facts)
        text += f"\n\nThings you know about the user:\n{lines}"
    return text