import pyttsx3
import speech_recognition as sr


def speak(text):
    # fresh engine each call avoids a pyttsx3 bug where it only talks once
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        try:
            audio = r.listen(source, timeout=8, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            print("Heard nothing.")
            return None
    try:
        return r.recognize_google(audio, language="en-US")
    except sr.UnknownValueError:
        print("Couldn't understand that.")
        return None
    except sr.RequestError as e:
        print(f"Speech service error: {e}")
        return None


speak("Hello Boss. Say something after the beep.")
heard = listen()
print(f"Heard: {heard}")
if heard:
    speak(f"You said: {heard}")