# main_window.py

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QDialog, QLineEdit, QPushButton, QLabel
from ttsback import ChatWorker  # Import the backend module
import configparser

import argparse

parser = argparse.ArgumentParser(prog="SteamUtils chat overlay")
parser.add_argument("video_ID", type=str, help="Video ID to use", default="https://www.youtube.com/watch?v=jfKfPfyJRdk")
parser.add_argument("-C", type=str, help="Config file to use", default="defaultconfig.ini")

args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.C)

def config2bool(s):
    if s in ["yes"]:
        return True
    if s in ["no"]:
        return False
    else:
        return None

class MainWindow(QWidget):
    """
    The main Frontend window to display chat messages.
    """
    def __init__(self, chat_worker: ChatWorker):
        super().__init__()
        self.chosen_link = None

        # Window setup
        self.setWindowTitle(config["Window"]["title"])  # Window title
        if not config2bool(config["Window"]["frame"]):
            self.setWindowFlag(Qt.FramelessWindowHint)  # No frame

        if not config2bool(config["Window"]["interactive"]):
            self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Noninteractive

        if config2bool(config["Window"]["ontop"]):
            self.setWindowFlag(Qt.WindowStaysOnTopHint)  # Alwaysontop

        self.setWindowOpacity(float(config["Window"]["opacity"]))  # Opactiy

        x = int(config["Window"]["x"])
        y = int(config["Window"]["y"])
        w = int(config["Window"]["width"])
        h = int(config["Window"]["height"])
        self.setGeometry(x, y, w, h)  # Geometry

        # Create the chatbox for displaying chat messages
        self.chatbox = QTextEdit("", self)

        if not config["Window"]["scrollbars"]:
            self.chatbox.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.chatbox.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        font = QFont(config["Window"]["font"], int(config["Window"]["fontsize"]), QFont.Normal)
        self.chatbox.setFont(font)

        # Layout setup
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.chatbox)
        self.setLayout(self.layout)

        # Assign the provided chat worker instance and start it
        self.worker = chat_worker
        self.worker.signal.connect(self.append_message)
        self.worker.start()  # Start the worker thread to fetch chat

    def append_message(self, txt):
        """
        Append new chat message to the chatbox and scroll to the bottom.
        """
        self.chatbox.append(txt)
        scrollbar = self.chatbox.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        if config2bool(config["Frontend"]["terminal_echo"]):
            print(txt)

    def close_event(self, event):
        """
        Handle window close event. Safely stop the worker thread.
        """
        self.worker.stop()
        
        self.worker.quit()
        self.worker.wait()  # Wait for the thread to finish
        event.accept()

class PopupDialog(QDialog):
    """
    A dialog window to prompt the user for the YouTube stream URL.
    """
    def __init__(self):
        super().__init__()
        self.submitted_yet = False  # Flag to track if the user has submitted the URL

        self.setWindowTitle("Enter Stream URL")
        self.setGeometry(100, 100, 300, 150)

        # Create layout and add widgets
        layout = QVBoxLayout()
        self.label = QLabel("Enter the URL or video ID of the livestream you want.\nThis URL can't be a replay or premiere", self)
        layout.addWidget(self.label)
        self.text_box = QLineEdit(self)
        layout.addWidget(self.text_box)
        self.submit_button = QPushButton("S U B M I T", self)
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)

    def on_submit(self):
        """
        Handles the submit action. Changes the video URL and restarts chat fetching.
        """
        self.chosen_link = self.text_box.text()
        # Create a new ChatWorker instance with the entered video URL
        self.submitted_yet = True
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    if config2bool(config["Startup"]["show_linkui"]):
        # Show the URL input dialog
        popup_window = PopupDialog()
        popup_window.show()
        app.exec_()

        chat_worker = ChatWorker(video_id=popup_window.chosen_link, flag_verbose_echo=False)
        if popup_window.chosen_link != None:
            main_window = MainWindow(chat_worker)
            main_window.show()
            sys.exit(app.exec_())
    
    else:
        chat_worker = ChatWorker(args.video_ID, config)
        main_window = MainWindow(chat_worker)
        main_window.show()
        app.exec_()
