import sys
import os
import subprocess
import webbrowser
import threading
import re

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtCore import Qt

import speech_recognition as sr
import pyttsx3

class VoiceAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Activated AI Assistant")
        self.setGeometry(100, 100, 500, 400)
        layout = QVBoxLayout()

        self.info_label = QLabel("Press 'Start Listening' and say a command:")
        layout.addWidget(self.info_label)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)

        self.listen_button = QPushButton("Start Listening")
        self.listen_button.clicked.connect(self.toggle_listening)
        layout.addWidget(self.listen_button)

        self.setLayout(layout)

        self.listening = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)

        self.listen_thread = None

    def toggle_listening(self):
        if not self.listening:
            self.listening = True
            self.listen_button.setText("Stop Listening")
            self.status_text.append("Listening started...")
            self.listen_thread = threading.Thread(target=self.listen_loop)
            self.listen_thread.start()
        else:
            self.listening = False
            self.listen_button.setText("Start Listening")
            self.status_text.append("Listening stopped.")

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_loop(self):
        while self.listening:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, phrase_time_limit=6)
                command = self.recognizer.recognize_google(audio)
                command = command.lower()
                self.status_text.append(f"You said: {command}")
                self.process_command(command)
            except sr.UnknownValueError:
                self.status_text.append("Sorry, I did not understand that.")
            except sr.RequestError:
                self.status_text.append("Could not request results; check your internet.")
            except Exception as e:
                self.status_text.append(f"Error: {str(e)}")

    def process_command(self, command):
        # Open folder command: e.g. "open folder downloads"
        if re.search(r'open folder (.+)', command):
            folder = re.findall(r'open folder (.+)', command)[0]
            self.status_text.append(f"Opening folder: {folder}")
            path = self.find_folder_path(folder)
            if path:
                os.startfile(path)
                self.speak(f"Opening folder {folder}")
            else:
                self.status_text.append(f"Folder not found: {folder}")
                self.speak(f"Folder {folder} not found")

        # Open file command: e.g. "open file example.txt"
        elif re.search(r'open file (.+)', command):
            filename = re.findall(r'open file (.+)', command)[0]
            self.status_text.append(f"Opening file: {filename}")
            path = self.find_file_path(filename)
            if path:
                os.startfile(path)
                self.speak(f"Opening file {filename}")
            else:
                self.status_text.append(f"File not found: {filename}")
                self.speak(f"File {filename} not found")

        # Open program: e.g. "open program calculator"
        elif re.search(r'open program (.+)', command):
            program = re.findall(r'open program (.+)', command)[0]
            self.status_text.append(f"Launching program: {program}")
            success = self.launch_program(program)
            if success:
                self.speak(f"Launching program {program}")
            else:
                self.status_text.append(f"Program {program} not found or failed to launch")
                self.speak(f"Program {program} not found or failed to launch")

        # Search web: e.g. "search for cats"
        elif re.search(r'search for (.+)', command):
            query = re.findall(r'search for (.+)', command)[0]
            url = "https://www.google.com/search?q=" + query.replace(" ", "+")
            self.status_text.append(f"Searching web for: {query}")
            webbrowser.open(url)
            self.speak(f"Searching for {query}")

        # Open website: e.g. "open website youtube.com"
        elif re.search(r'open website (.+)', command):
            website = re.findall(r'open website (.+)', command)[0]
            if not website.startswith("http"):
                website = "https://" + website
            self.status_text.append(f"Opening website: {website}")
            webbrowser.open(website)
            self.speak(f"Opening website {website}")

        else:
            self.status_text.append(f"Command not recognized: {command}")
            self.speak("Sorry, I did not understand that command.")

    def find_folder_path(self, folder_name):
        # Try common user folders in Windows
        from pathlib import Path
        user_dirs = ["Desktop", "Downloads", "Documents", "Pictures", "Music", "Videos"]
        home = str(Path.home())
        for d in user_dirs:
            if folder_name.lower() in d.lower():
                folder_path = os.path.join(home, d)
                if os.path.exists(folder_path):
                    return folder_path
        # If exact folder name given relative to home directory
        possible_path = os.path.join(home, folder_name)
        if os.path.exists(possible_path):
            return possible_path
        return None

    def find_file_path(self, filename):
        # Search in user's home directory and desktop for simplicity
        from pathlib import Path
        home = str(Path.home())
        search_dirs = [home, os.path.join(home, "Desktop")]
        for directory in search_dirs:
            for root, dirs, files in os.walk(directory):
                if filename.lower() in (f.lower() for f in files):
                    return os.path.join(root, filename)
        return None

    def launch_program(self, program_name):
        # Map some common program names to executable paths or commands
        program_map = {
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe",
            "word": r"C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "excel": r"C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "chrome": r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            # Add more mappings if needed
        }
        exe = program_map.get(program_name.lower())
        if exe:
            try:
                subprocess.Popen(exe)
                return True
            except Exception as e:
                self.status_text.append(f"Error launching {program_name}: {str(e)}")
                return False
        else:
            # Try launching by name directly
            try:
                subprocess.Popen(program_name)
                return True
            except Exception as e:
                self.status_text.append(f"Error launching {program_name}: {str(e)}")
                return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = VoiceAssistant()
    assistant.show()
    sys.exit(app.exec_())

