def confirm(question: str) -> bool:
    """Ask the user to approve an action. Anything but y/yes counts as no."""
    print(f"\n[CONFIRM] {question}")
    while True:
        answer = input("Allow? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no", ""):
            return False
        print("Please type y or n.")