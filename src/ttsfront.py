# main_window.py

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QDialog, QLineEdit, QPushButton, QLabel
from ttsback import ChatWorker  # Import the backend module

import argparse

parser = argparse.ArgumentParser(prog="SteamUtils chat overlay")
parser.add_argument("-X", type=int, help="The X position of the window", default=0)
parser.add_argument("-Y", type=int, help="The Y position of the window", default=0)
parser.add_argument("-W", type=int, help="The width of the window", default=320)
parser.add_argument("-H", type=int, help="The height of the window", default=180)
parser.add_argument("-O", type=float, help="Opacity", default=0.7)

parser.add_argument("--title", type=str, help="The title of the window", default="Dave From Seattle")

parser.add_argument("-noninteractive", action="store_true", help="The window is uninteractable")
parser.add_argument("-no_frame", action="store_true", help="The window has no frame")
parser.add_argument("-always_ontop", action="store_true", help="The window has no frame")
parser.add_argument("-no_scrollbars", action="store_true", help="The QTextEdit has no scroll bars")

parser.add_argument("-linkui", action="store_true", help="Opens LinkUI window to chose the livestream")

parser.add_argument("-echo_to_terminal", action="store_true", help="Echos the messages to the terminal")
parser.add_argument("-v", action="store_true", help="Echoed messages are verbose")

parser.add_argument("video_ID", type=str, help="Video ID to use", default="https://www.youtube.com/watch?v=jfKfPfyJRdk")
args = parser.parse_args()

class MainWindow(QWidget):
    """
    The main Frontend window to display chat messages.
    """
    def __init__(self, chat_worker: ChatWorker):
        super().__init__()

        # Window setup
        self.setWindowTitle(args.title)  # Window title
        if args.no_frame:
            self.setWindowFlag(Qt.FramelessWindowHint)  # No frame

        if args.noninteractive:
            self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Noninteractive

        if args.always_ontop:
            self.setWindowFlag(Qt.WindowStaysOnTopHint)  # Alwaysontop

        self.setWindowOpacity(args.O)  # Opactiy
        self.setGeometry(args.X, args.Y, args.W, args.H)  # Geometry

        # Create the chatbox for displaying chat messages
        self.chatbox = QTextEdit("", self)

        if args.no_scrollbars:
            self.chatbox.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.chatbox.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        font = QFont("monospace", 9, QFont.Normal)
        self.chatbox.setFont(font)

        # Layout setup
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.chatbox)
        self.setLayout(self.layout)

        # Assign the provided chat worker instance and start it
        self.worker = chat_worker
        self.worker.update_signal.connect(self.append_message)
        self.worker.start()  # Start the worker thread to fetch chat

    def append_message(self, txt):
        """
        Append new chat message to the chatbox and scroll to the bottom.
        """
        self.chatbox.append(txt)
        scrollbar = self.chatbox.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        if args.echo_to_terminal:
            print(txt)

    def close_event(self, event):
        """
        Handle window close event. Safely stop the worker thread.
        """
        self.worker.stop()  # Stop the chat fetching thread
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
        entered_text = self.text_box.text()
        # Create a new ChatWorker instance with the entered video URL
        self.chat_worker = ChatWorker(video_id=entered_text)  
        self.submitted_yet = True
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    if args.linkui:
        # Show the URL input dialog
        popup_window = PopupDialog()
        popup_window.show()
        app.exec_()

        main_window = MainWindow(popup_window.chat_worker)
        main_window.show()
        sys.exit(app.exec_())
    
    else:
        chat_worker = ChatWorker(args.video_ID, args.v)
        main_window = MainWindow(chat_worker)
        main_window.show()
        sys.exit(app.exec_())
