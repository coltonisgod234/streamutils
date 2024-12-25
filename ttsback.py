# chat_fetcher.py

import pytchat
import emoji
from PyQt5.QtCore import QThread, pyqtSignal
import commands

class ChatWorker(QThread):
    """
    Worker QThread for receiving chat messages while the GUI runs.
    This class fetches messages and processes commands.
    """
    update_signal = pyqtSignal(str)  # Signal to send data back to the main thread

    def __init__(self, video_id: str):
        super().__init__()
        self.video_id = video_id
        self.chat = pytchat.create(video_id=self.video_id)
        self.running = True  # Flag to keep the thread running

    def check_if_chat_alive(self):
        """
        Checks if the YouTube chat is alive.
        """
        return self.chat.is_alive()

    def run(self):
        """
        Starts the thread and continuously fetches messages from the chat.
        """
        self.update_signal.emit("Chat app is READY!")
        while self.running:
            QThread.msleep(1000)  # Wait for 1 second before fetching new chat messages
            for c in self.chat.get().sync_items():
                emoji_message = emoji.emojize(c.message)  # Convert emojis to unicode
                self.update_signal.emit(f"[{c.author.name}]:  {emoji_message}")  # Send message to GUI

                # Check for specific commands
                if emoji_message.startswith("/tts"):
                    commands.tts(emoji_message)

    def stop(self):
        """
        Stop the chat fetching thread.
        """
        self.running = False
        self.wait()  # Wait for the thread to finish

    def set_video_id(self, video_id: str):
        """
        Change the video ID and restart the chat.
        """
        self.video_id = video_id
        self.chat = pytchat.create(video_id=self.video_id)
