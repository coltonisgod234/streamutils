# chat_fetcher.py

import pytchat
# import emoji
from PyQt5.QtCore import QThread, pyqtSignal
import plugins
import emoji
import time

def config2bool(s):
    if s in ["yes"]:
        return True
    if s in ["no"]:
        return False
    else:
        return None

def convert_message(msg: str, c, verbose: bool) -> tuple[str, str]:
    emoji_message = emoji.emojize(msg)  # Convert emojis from markdown to unicode

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
    signal = pyqtSignal(str)  # Signal to send data back to the main thread

    def __init__(self, video_id: str, config: dict):
        super().__init__()
        self.video_id = video_id
        self.verbose = config2bool(config["Frontend"]["verbose"])
        self.config = config
        self.chat = pytchat.create(video_id=self.video_id)
        self.running = True  # Flag to keep the thread running
        self.plugin_manager = plugins.PluginManager(config["Plugins"]["directory"])  # Manage plugins

    def check_if_chat_alive(self):
        """
        Checks if the YouTube chat is alive.
        """
        return self.chat.is_alive()

    def startup(self):
        # Initalize all plugins
        self.plugin_manager.load_plugins(self.signal)
        self.plugin_manager.initalize_plugins(self.signal)
        self.plugin_manager.configure_plugins(self.signal)
        self.signal.emit("OK.")
    
    def startup_verbose(self):
        # Initalize all plugins
        self.signal.emit("Streamutils \"Dave From Seattle\" backend init...")
        self.signal.emit(f"Dumped configuration below")
        a = ""
        for section in self.config.sections():
            a += f"[{section}]  "
            for key, value in self.config.items(section):
                a += (f"{key}={value};")
            
        self.signal.emit(a)

        self.signal.emit(f"Begining plugin init...")

        self.signal.emit("Loading plugins...")
        self.plugin_manager.load_plugins(self.signal)
        self.signal.emit("Initalizing plugins...")
        self.plugin_manager.initalize_plugins(self.signal)
        self.signal.emit("Configuring plugins...")
        self.plugin_manager.configure_plugins(self.signal)
        self.signal.emit("Ready to get chat messages. OK.")

    def plugins_main(self):
        for name, plugin in self.plugin_manager.plugins.items():
            try:
                plugin.event_main(time.time_ns())

            except Exception as e:
                print(f"{name} error'd but honestly we're just gonna ignore it, {e}")

    def message_notify(self, message):
        for name, plugin in self.plugin_manager.plugins.items():
            try: plugin.event_message(c)
            except Exception as e: print(f"{name} error'd but honestly it's a plugin who cares, {e}")

    def run(self):
        """
        Starts the thread and continuously fetches messages from the chat.
        """
        self.startup()
        # While running, we fetch chat messages
        while self.running:
            QThread.usleep(int(self.config["Backend"]["loop_wait_ns"]))
            if config2bool(self.config["Plugins"]["enable_pluginmain"]): self.plugins_main()
            for c in self.chat.get().sync_items():
                # Process the message
                msg, formatted_msg = convert_message(c.message, c, self.verbose)
                self.signal.emit(formatted_msg)  # Update the GUI

                # Notify plugins
                self.message_notify(msg)

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
