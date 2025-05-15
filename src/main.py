import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QComboBox, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import speech_recognition as sr
import pyaudio
import threading


from src.gui.app_window import Window

class MIdnight(QMainWindow):

    _window = None

    def __init__(self):

        self._window = Window()
        pass
    #enddef




class VoiceInterpreter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Voice Interpreter")
        self.showMaximized()

        self.create_toolbar()
        self.create_main_content()

    def create_toolbar(self):
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)

        self.model_combo = QComboBox(toolbar)
        self.model_combo.addItem("Google Speech Recognition")
        self.model_combo.addItem("Microsoft Azure Speech Services")
        toolbar.addWidget(self.model_combo)

        self.start_button = toolbar.addAction("Start")
        self.start_button.triggered.connect(self.start_recognition)

        self.stop_button = toolbar.addAction("Stop")
        self.stop_button.triggered.connect(self.stop_recognition)

    def create_main_content(self):
        main_content = QWidget(self)
        self.setCentralWidget(main_content)

        layout = QVBoxLayout()
        main_content.setLayout(layout)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.small_widget = QTextEdit()
        self.small_widget.setFixedSize(200, 50)
        layout.addWidget(self.small_widget)

    def start_recognition(self):
        self.recognition_thread = threading.Thread(target=self.recognize_speech)
        self.recognition_thread.start()

    def stop_recognition(self):
        self.recognition_thread.join()

    def recognize_speech(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Please say something:")
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language="en-US")
                self.text_edit.setText(text)
                self.small_widget.setText(text)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    voice_interpreter = VoiceInterpreter()
    voice_interpreter.show()
    sys.exit(app.exec_())
