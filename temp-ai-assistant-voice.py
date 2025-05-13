import speech_recognition as sr
import threading

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False

    def start_listening(self):
        self.listening = True
        threading.Thread(target=self.listen).start()

    def listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                audio = self.recognizer.listen(source)
                try:
                    command = self.recognizer.recognize_google(audio)
                    self.process_command(command)
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError:
                    print("Could not request results")

    def process_command(self, command):
        # Analyze and execute command
        print(f"Command recognized: {command}")
        # Add command execution logic here
