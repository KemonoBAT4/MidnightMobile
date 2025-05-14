
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser

from src.assistant.interpreter import Interpreter

class VoiceAssistant:

    _interpreter = None

    _engine = None
    _recognizer = None
    _microphone = None
    _listening = False

    def __init__(self):
        self.interpreter = Interpreter()
        self._engine = pyttsx3.init()
        voices = self._engine.getProperty('voices')
        self._engine.setProperty('voice', voices[0].id)

        self._recognizer = sr.Recognizer()
        # self._microphone = sr.Microphone()
        self._listening = False
    #enddef
#endclass



class VoiceAssistant:
    def __init__(self):
        # Initialize the speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)  # set voice, 0 or 1 for male/female depending on system

        # Initialize recognizer
        self.recognizer = sr.Recognizer()

        # Internal flag for usage control if needed
        self.is_listening = False

    def speak(self, text):
        """Speak out the text."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_once(self, timeout=5, phrase_time_limit=5):
        """
        Listen once from the microphone and return recognized text.
        Returns empty string if nothing recognized.
        """
        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                command = self.recognizer.recognize_google(audio)
                return command.lower()
            except sr.WaitTimeoutError:
                # Could not hear anything in timeout seconds
                return ""
            except sr.UnknownValueError:
                # Speech was unintelligible
                self.speak("Sorry, I did not understand that.")
                return ""
            except sr.RequestError:
                self.speak("Sorry, my speech service is down.")
                return ""

    def respond(self, command):
        """
        Respond based on the recognized command string.
        Returns False if a quit/exit command received, True otherwise.
        """
        if not command:
            return True  # no command to respond to

        if 'hello' in command:
            self.speak("Hello! How can I help you today?")
        elif 'time' in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {now}")
        elif 'open youtube' in command:
            self.speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        elif 'exit' in command or 'quit' in command:
            self.speak("Goodbye!")
            return False
        else:
            self.speak("Sorry, I can't perform that command yet.")
        return True




'''

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser


class VoiceAssistant:
    def __init__(self):
        # Initialize the speech engine
        self.engine = pyttsx3.init()
        # Set voice properties (optional)
        voices = self.engine.getProperty('voices')
        # Set to a male or female voice as available
        self.engine.setProperty('voice', voices[0].id)

        # Initialize recognizer
        self.recognizer = sr.Recognizer()

    def speak(self, text):
        """Speak out the text."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listen to microphone and return recognized text."""
        with sr.Microphone() as source:
            print("Listening...")
            # adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = self.recognizer.listen(source, phrase_time_limit=5)
        try:
            print("Recognizing...")
            command = self.recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            self.speak("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            self.speak("Sorry, my speech service is down.")
            return ""

    def respond(self, command):
        """Respond to user commands."""
        if 'hello' in command:
            self.speak("Hello! How can I help you today?")
        elif 'time' in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {now}")
        elif 'open youtube' in command:
            self.speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        elif 'exit' in command or 'quit' in command:
            self.speak("Goodbye!")
            return False
        else:
            self.speak("Sorry, I can't perform that command yet.")
        return True


def main():
    assistant = VoiceAssistant()
    assistant.speak("Voice assistant started. Say something.")
    running = True
    while running:
        command = assistant.listen()
        if command:
            running = assistant.respond(command)


if __name__ == "__main__":
    main()


'''