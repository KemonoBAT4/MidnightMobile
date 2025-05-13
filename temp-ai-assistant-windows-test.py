import sys
import os
import subprocess
import webbrowser
import threading
import re

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QHBoxLayout
)
from PyQt5.QtCore import Qt

import speech_recognition as sr
import pyttsx3


class VoiceAssistantGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice & GUI Activated AI Assistant")
        self.setGeometry(100, 100, 600, 450)
        self.init_ui()

        self.listening = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        self.listen_thread = None

    def init_ui(self):
        layout = QVBoxLayout()

        self.info_label = QLabel("Use voice or type commands below and press Execute:")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # Text edit for logs/status
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: #f7f7f7;
                font-family: Consolas, monospace;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.status_text, stretch=5)

        # Horizontal layout for text input + button
        input_layout = QHBoxLayout()

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type a command here...")
        input_layout.addWidget(self.command_input, stretch=4)

        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.on_execute_clicked)
        input_layout.addWidget(self.execute_button, stretch=1)

        layout.addLayout(input_layout)

        # Button to start/stop voice listening
        self.listen_button = QPushButton("Start Listening")
        self.listen_button.clicked.connect(self.toggle_listening)
        self.listen_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(self.listen_button)

        self.setLayout(layout)

    def append_status(self, text):
        self.status_text.append(text)
        # Auto scroll to bottom
        self.status_text.verticalScrollBar().setValue(self.status_text.verticalScrollBar().maximum())

    def toggle_listening(self):
        if not self.listening:
            self.listening = True
            self.listen_button.setText("Stop Listening")
            self.append_status("Listening started...")
            self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
            self.listen_thread.start()
        else:
            self.listening = False
            self.listen_button.setText("Start Listening")
            self.append_status("Listening stopped.")

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
                self.append_status(f"[Voice] You said: {command}")
                self.process_command(command)
            except sr.UnknownValueError:
                self.append_status("[Voice] Sorry, I did not understand that.")
            except sr.RequestError:
                self.append_status("[Voice] Could not request results; check your internet.")
            except Exception as e:
                self.append_status(f"[Voice] Error: {str(e)}")

    def on_execute_clicked(self):
        command = self.command_input.text().strip().lower()
        if command:
            self.append_status(f"[Text] Executing command: {command}")
            self.process_command(command)
            self.command_input.clear()
        else:
            self.append_status("[Text] Please enter a command.")

    def process_command(self, command):
        # Open folder command: e.g. "open folder downloads"
        import pathlib

        def find_folder_path(folder_name):
            user_dirs = ["Desktop", "Downloads", "Documents", "Pictures", "Music", "Videos"]
            home = str(pathlib.Path.home())
            for d in user_dirs:
                if folder_name in d.lower() or folder_name == d.lower():
                    folder_path = os.path.join(home, d)
                    if os.path.exists(folder_path):
                        return folder_path
            possible_path = os.path.join(home, folder_name)
            if os.path.exists(possible_path):
                return possible_path
            return None

        def find_file_path(filename):
            home = str(pathlib.Path.home())
            search_dirs = [home, os.path.join(home, "Desktop")]
            for directory in search_dirs:
                for root, dirs, files in os.walk(directory):
                    if filename in (f.lower() for f in files):
                        return os.path.join(root, filename)
            return None

        def launch_program(program_name):
            program_map = {
                "calculator": "calc.exe",
                "notepad": "notepad.exe",
                "paint": "mspaint.exe",
                "word": r"C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
                "excel": r"C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
                "chrome": r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            }
            exe = program_map.get(program_name)
            if exe:
                try:
                    subprocess.Popen(exe)
                    return True
                except Exception as e:
                    self.append_status(f"Error launching {program_name}: {str(e)}")
                    return False
            else:
                try:
                    subprocess.Popen(program_name)
                    return True
                except Exception as e:
                    self.append_status(f"Error launching {program_name}: {str(e)}")
                    return False

        # Process commands stepwise
        if 'open folder' in command:
            match = re.search(r'open folder (.+)', command)
            if match:
                folder = match.group(1)
                path = find_folder_path(folder)
                if path:
                    os.startfile(path)
                    self.append_status(f"Opening folder: {folder}")
                    self.speak(f"Opening folder {folder}")
                else:
                    self.append_status(f"Folder not found: {folder}")
                    self.speak(f"Folder {folder} not found")
            return

        if 'open file' in command:
            match = re.search(r'open file (.+)', command)
            if match:
                filename = match.group(1)
                path = find_file_path(filename)
                if path:
                    os.startfile(path)
                    self.append_status(f"Opening file: {filename}")
                    self.speak(f"Opening file {filename}")
                else:
                    self.append_status(f"File not found: {filename}")
                    self.speak(f"File {filename} not found")
            return

        if 'open program' in command:
            match = re.search(r'open program (.+)', command)
            if match:
                program = match.group(1)
                success = launch_program(program)
                if success:
                    self.append_status(f"Launching program: {program}")
                    self.speak(f"Launching program {program}")
                else:
                    self.append_status(f"Could not launch program: {program}")
                    self.speak(f"Could not launch program {program}")
            return

        if 'search for' in command:
            match = re.search(r'search for (.+)', command)
            if match:
                query = match.group(1)
                url = "https://www.google.com/search?q=" + query.replace(" ", "+")
                webbrowser.open(url)
                self.append_status(f"Searching web for: {query}")
                self.speak(f"Searching for {query}")
            return

        if 'open website' in command:
            match = re.search(r'open website (.+)', command)
            if match:
                website = match.group(1)
                if not website.startswith("http"):
                    website = "https://" + website
                webbrowser.open(website)
                self.append_status(f"Opening website: {website}")
                self.speak(f"Opening website {website}")
            return

        self.append_status(f"Command not recognized: {command}")
        self.speak("Sorry, I did not understand that command.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = VoiceAssistantGUI()
    assistant.show()
    sys.exit(app.exec_())

