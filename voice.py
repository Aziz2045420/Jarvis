import re
import pyttsx3
import speech_recognition as sr

EXIT_WORDS = ("exit", "goodbye", "shut down", "shutdown", "quit")
PREFERRED_VOICE = "David"   # or "Zira"
VOICE_RATE = 175            # words per minute, default is ~200


def clean_for_speech(text):
    """Strip markdown symbols so the voice doesn't read 'asterisk asterisk'."""
    text = re.sub(r"[*_`#>]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def pick_voice(engine):
    """Return the id of the preferred English voice, else any English voice."""
    voices = engine.getProperty("voices")
    for v in voices:
        if PREFERRED_VOICE.lower() in v.name.lower():
            return v.id
    for v in voices:
        if "english" in v.name.lower():
            return v.id
    return None


def speak(text):
    # fresh engine each call avoids the pyttsx3 "only talks once" bug
    engine = pyttsx3.init()
    voice_id = pick_voice(engine)
    if voice_id:
        engine.setProperty("voice", voice_id)
    else:
        print("[no English voice found, using default]")
    engine.setProperty("rate", VOICE_RATE)
    engine.say(clean_for_speech(text))
    engine.runAndWait()


def listen(recognizer):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("[listening...]")
        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=20)
        except sr.WaitTimeoutError:
            return None
    try:
        return recognizer.recognize_google(audio, language="en-US")
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"[speech service error: {e}]")
        return None