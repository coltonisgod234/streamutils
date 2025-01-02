# chat_fetcher.py

import pytchat
# import emoji
from PyQt5.QtCore import QThread, pyqtSignal
import plugins

def convert_message(msg: str, c, verbose: bool) -> tuple[str, str]:
    emoji_message = msg # emoji.emojize(msg)  # Convert emojis from markdown to unicode

    if verbose:
        gui_message = f"""
        ---Msg:  {c.message}
        ---Meta: type={c.type} id={c.id}
        ---Time: timestamp={c.timestamp} datetime={c.datetime}
        ---Auth: authName={c.author.name} authChID={c.author.channelId} authVerif={c.author.isVerified} authOwn={c.author.isChatOwner} authMod?={c.author.isChatModerator} authSp={c.author.isChatSponsor}
        """

    else:
        gui_message = f"[{c.author.name}]:  {emoji_message}"  # For the GUI

    return (emoji_message, gui_message)

class ChatWorker(QThread):
    """
    Worker QThread for receiving chat messages while the GUI runs.
    This class fetches messages and processes commands.
    """
    update_signal = pyqtSignal(str)  # Signal to send data back to the main thread

    def __init__(self, video_id: str, flag_verbose_echo: bool):
        super().__init__()
        self.video_id = video_id
        self.verbose = flag_verbose_echo
        self.chat = pytchat.create(video_id=self.video_id)
        self.running = True  # Flag to keep the thread running
        self.plugin_manager = plugins.PluginManager("plugins")  # Manage plugins

    def check_if_chat_alive(self):
        """
        Checks if the YouTube chat is alive.
        """
        return self.chat.is_alive()

    def run(self):
        """
        Starts the thread and continuously fetches messages from the chat.
        """
        # Initalize all plugins
        self.plugin_manager.load_plugins()
        self.plugin_manager.initalize_plugins()

        # While running, we fetch chat messages
        while self.running:
            QThread.msleep(250)  # Wait before fetching new chat messages
            for c in self.chat.get().sync_items():
                # Process the message
                msg, formatted_msg = convert_message(c.message, c, self.verbose)
                self.update_signal.emit(formatted_msg)  # Update the GUI

                # Notify plugins
                for plugin in self.plugin_manager.plugins:
                    plugin.event_message(c)
                
    def stop(self):
        """
        Stop the chat fetching thread.
        """
        self.plugin_manager.unload_plugins()
        self.running = False
        # self.wait()  # Wait for the thread to finish

    def set_video_id(self, video_id: str):
        """
        Change the video ID and restart the chat.
        """
        self.video_id = video_id
        self.chat = pytchat.create(video_id=self.video_id)
