# main_window.py

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QDialog, QLineEdit, QPushButton, QLabel
from ttsback import ChatWorker
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

import argparse

import logging

logger_chatworker = logging.getLogger("ChatWorker")
logger_frontend = logging.getLogger("Frontend")

parser = argparse.ArgumentParser(prog="Steamutils chat overlay (AKA. Dave From Seattle)")
parser.add_argument("video_ID", type=str, help="Video ID to use", default="https://www.youtube.com/watch?v=jfKfPfyJRdk")
parser.add_argument("-C", type=str, help="Config file to use", required=True)

args = parser.parse_args()

logging.basicConfig(
    level=logging.INFO,  # Global level: we can override this for specific loggers
    format='[ %(asctime)15s | %(name)15s | %(levelname)8s ]\t\t %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

config = configparser.ConfigParser()
config.read(args.C)
logging.info(f"Read configuration {args.C}")

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

        if config["Window"]["scrollbars"]:
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

        # Assign the worker a signal
        self.worker.msg_signal.connect(self.append_message)
        self.worker.start()  # Start the worker thread to fetch chat

    def append_message(self, txt):
        """
        Append new chat message to the chatbox and scroll to the bottom.
        """
        self.chatbox.append(txt)
        scrollbar = self.chatbox.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        if config2bool(config["Frontend"]["terminal_echo"]):
            logging.info(f"Echoed to terminal: {txt}")

    def closeEvent(self, event):
        """
        Handle window close event. Safely stop the worker thread.
        """
        logging.error("Got closeEvent, did you close the window? Running cleanup...")
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
        self.layoutdef = QVBoxLayout()
        self.label = QLabel("Enter the URL or video ID of the livestream you want.\nThis URL can't be a replay or premiere", self)
        self.layoutdef.addWidget(self.label)
        self.text_box = QLineEdit(self)
        self.layoutdef.addWidget(self.text_box)
        self.submit_button = QPushButton("S U B M I T", self)
        self.cancel_button = QPushButton("C A N C E L", self)

        self.submit_button.clicked.connect(self.on_submit)
        self.cancel_button.clicked.connect(self.on_cancel)
        self.layoutdef.addWidget(self.submit_button)
        self.layoutdef.addWidget(self.cancel_button)
        self.setLayout(self.layoutdef)

    def on_submit(self):
        """
        Handles the submit action. Changes the video URL and restarts chat fetching.
        """
        self.link = self.text_box.text()
        # Create a new ChatWorker instance with the entered video URL
        self.submitted_yet = True
        self.accept()
    
    def on_cancel(self):
        sys.exit(1)

def entrypoint(video_id):
    console_title = config["Window"].get("console_title", fallback="Dave From Seattle (CONSOLE)")
    print(f"\33]0;{console_title}\a", end="", flush=True)

    app = QApplication(sys.argv)

    chat_worker = ChatWorker(video_id, config)
    main_window = MainWindow(chat_worker)
    main_window.show()

    logging.info("This is the console window! It's not the main application, you can minimize it safely unless you need the debugging information")
    app.exec_()

    logging.fatal("The application appears to have terminated or shut down. Exiting with code 0...")
    exit(0)

def run_linkui(additional_msg=None):
    while True:
        dialog = linkui_dialog(additional_msg)
        if dialog.link in [None, ""]:
            continue
        else:
            break

    entrypoint(dialog.link)

def linkui_dialog(additional_msg=None):
    app = QApplication(sys.argv)

    dialog = PopupDialog()

    if additional_msg is not None:
        lbl = QLabel(f"Message: {additional_msg}")
        dialog.layoutdef.addWidget(lbl)

    dialog.show()
    app.exec_()

    return dialog

def get_user_stream(channelid):
    logging.info("Autodetecting livestream URL...")
    logging.info(f"Channel ID is {channelid}")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Headless mode
    options.add_argument("--disable-gpu")

    logging.info("Creating selenium instance...", end="")
    driver = webdriver.Chrome(options=options)
    logging.info("OK.")

    url = f"https://www.youtube.com/channel/{channelid}/live"
    driver.get(url)

    logging.info("Waiting for youtube to finish loading")
    time.sleep(1)

    logging.info("Hopefully it's done.")
    finalurl = driver.current_url
    logging.info(f"Final URL is `{finalurl}`... ", end="")

    if '/live' in finalurl:
        # If we're still on the /live page, the user isn't live
        logging.error("The user is not live")
        driver.quit()
        return None
    else:
        # If we're not on the /live page, the user is live and we can get the link
        videoid = finalurl.split('v=')[1]
        driver.quit()
        logging.info(f"The user is live, ID: {videoid}")
        return f"https://www.youtube.com/watch?v={videoid}"

def run_autofetch():
    try: channelid = config["Startup"]["channelid"]
    except KeyError:
        logging.fatal("Attempted to run in autofetch mode, but channelid is not set. Unsure what to do. Exiting with code 2")
        sys.exit(2)

    url = get_user_stream(channelid)
    if url is None:
        run_linkui("Configured user isn't streaming, falling back to linkui")
    
    entrypoint(url)

if __name__ == "__main__":
    if config["Startup"]["startup_mode"] == "linkui":
        run_linkui()
    elif config["Startup"]["startup_mode"] == "autofetch":
        run_autofetch()
    elif config["Startup"]["startup_mode"] == "none":
        entrypoint(args.video_ID)
    else:
        logging.fatal("Invalid startup mode. Unsure what to do. Exiting with code 4.")
        sys.exit(4)
