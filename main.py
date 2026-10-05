import os
import time
import speech_recognition as sr
from google import genai
from google.genai import types, errors

import actions
import files
import memory
import tools
import voice

# ---------- Gemini ----------
MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
]
ROUNDS = 2
SKIP_CODES = (404, 429, 500, 503, 504)

SYSTEM_PROMPT = (
    "You are JARVIS, a personal assistant. Address the user as 'Boss'. "
    "Be concise, direct, and a little witty. "
    "Your replies may be spoken aloud, so avoid markdown, bullet symbols and emojis, "
    "and keep answers short unless asked for detail. "
    "You have tools to list folders, read text files and search files on the user's PC. "
    "Use them whenever the user asks about their files. Never guess file contents or names. "
    "If a tool returns an error, tell the user plainly what went wrong. "
    "You also have memory tools. Use remember when the user asks you to remember something "
    "or shares a lasting fact about themselves. Never save passwords, API keys, or other "
    "secrets. Use list_memories and forget when asked what you know or to forget something. "
    "Use get_weather for weather questions; if the user names no city, use the city you "
    "know they live in, otherwise ask which city. Say temperatures in degrees Celsius. "
    "You CAN open websites: call open_website whenever the user asks to open a site or "
    "search the web (for a search, open https://www.google.com/search?q=<terms>). "
    "You CAN open apps with open_app and create new text files with create_text_file "
    "(saved in the workspace folder). The tools ask the user for confirmation themselves, "
    "so do not ask for permission first, just call the tool. If a tool says the user "
    "declined, accept it, say OK, and do not try again. You cannot delete or overwrite files. "
    "Never say you cannot open a browser."
)

TOOLS = [
    files.list_folder,
    files.read_text_file,
    files.search_files,
    memory.remember,
    memory.list_memories,
    memory.forget,
    tools.get_datetime,
    tools.get_weather,
    tools.open_website,
    actions.open_app,
    actions.create_text_file,
]


def make_config():
    """Rebuilt every message so newly saved memories and the time are fresh."""
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT + memory.memory_prompt(),
        tools=TOOLS,
    )


def ask(client, state, text):
    """Try each model in order, carrying the conversation history along."""
    for round_no in range(1, ROUNDS + 1):
        for model in MODELS:
            history = state["chat"].get_history() if state["chat"] else None
            chat = client.chats.create(model=model, config=make_config(), history=history)
            try:
                reply = chat.send_message(text).text
            except errors.APIError as e:
                if e.code in SKIP_CODES:
                    continue
                return f"Error talking to Gemini: {e}"
            state["chat"] = chat
            if model != MODELS[0]:
                print(f"(answered by {model})")
            return reply or "(empty reply)"
        if round_no < ROUNDS:
            wait = 3 * round_no
            print(f"JARVIS: Everything is busy, waiting {wait}s and retrying...")
            time.sleep(wait)
    return "Every model is overloaded right now, Boss. Try again in a minute."


def reply(client, state, text, voice_mode):
    answer = ask(client, state, text)
    print(f"JARVIS: {answer}\n")
    if voice_mode:
        voice.speak(answer)


def main():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set in this session")

    client = genai.Client(api_key=key)
    recognizer = sr.Recognizer()
    state = {"chat": None}
    voice_mode = False

    print("================================")
    print("        JARVIS ONLINE")
    print("================================")
    print("Hello Boss. I am JARVIS.")
    print("Type 'voice' for voice mode, 'text' to go back, 'exit' to quit.")
    print("In voice mode say 'text mode' or 'goodbye'. Ctrl+C also quits.\n")

    try:
        while True:
            if voice_mode:
                user_input = voice.listen(recognizer)
                if not user_input:
                    continue
                print(f"You (voice): {user_input}")
            else:
                user_input = input("You: ").strip()
                if not user_input:
                    continue

            low = user_input.lower().strip(" .!?")

            if low in voice.EXIT_WORDS:
                print("JARVIS: Shutting down. Goodbye.")
                if voice_mode:
                    voice.speak("Shutting down. Goodbye.")
                break
            if low in ("voice", "voice mode"):
                voice_mode = True
                print("JARVIS: Voice mode on.\n")
                voice.speak("Voice mode on. I'm listening, Boss.")
                continue
            if low in ("text", "text mode"):
                voice_mode = False
                print("JARVIS: Text mode.\n")
                voice.speak("Back to text mode.")
                continue

            reply(client, state, user_input, voice_mode)
    except KeyboardInterrupt:
        print("\nJARVIS: Shutting down. Goodbye.")


if __name__ == "__main__":
    main()