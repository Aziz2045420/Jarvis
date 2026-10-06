_handler = None


def set_handler(fn):
    """Use fn(question) -> bool instead of the terminal prompt (the web UI sets this)."""
    global _handler
    _handler = fn


def confirm(question: str) -> bool:
    """Ask the user to approve an action. Anything but y/yes counts as no."""
    if _handler is not None:
        try:
            return bool(_handler(question))
        except Exception:
            return False
    print(f"\n[CONFIRM] {question}")
    while True:
        answer = input("Allow? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no", ""):
            return False
        print("Please type y or n.")