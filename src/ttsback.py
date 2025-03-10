# chat_fetcher.py

import pytchat
# import emoji
from PyQt5.QtCore import QThread, pyqtSignal
import plugins
import emoji
import time
import os
import logging

def config2bool(s):
    if s in ["yes"]:
        return True
    if s in ["no"]:
        return False
    else:
        return None

def convert_message(c, config) -> tuple[str, str]:
    c.message = emoji.emojize(c.message)  # Sorry

    if config2bool(config["Frontend"]["verbose"]):
        gui_message = f"""
        ---Msg:  {c.message}
        ---Meta: type={c.type} id={c.id}
        ---Time: timestamp={c.timestamp} datetime={c.datetime}
        ---Auth: authName={c.author.name} authChID={c.author.channelId} authVerif={c.author.isVerified} authOwn={c.author.isChatOwner} authMod?={c.author.isChatModerator} authSp={c.author.isChatSponsor}
        """

    elif c.type == "superChat":
        gui_message = config["Frontend.messageTemplates"]["superChat"].format(msg=c)

    elif c.type == "textMessage":
        gui_message = config["Frontend.messageTemplates"]["textMessage"].format(msg=c)
    
    else:
        gui_message = "Unregognized message type, not textMessage or superChat?"

    return gui_message

class ChatWorker(QThread):
    """
    Worker QThread for receiving chat messages while the GUI runs.
    This class fetches messages and processes commands.
    """
    msg_signal = pyqtSignal(str)  # send messages back to the GUI

    def __init__(self, video_id: str, config: dict):
        super().__init__()
        self.video_id = video_id
        self.verbose = config2bool(config["Frontend"]["verbose"])
        self.config = config
        self.chat = pytchat.create(video_id=self.video_id)
        self.running = True  # Flag to keep the thread running
        try: self.installdir = config["Plugins.Paths"]["installdir"]
        except KeyError: self.installdir = None

        self.logger = logging.getLogger("chatworker")
        self.logger.setLevel(logging.INFO)
        pluginmgr_logger = logging.getLogger("pluginmgr")
        pluginmgr_logger.setLevel(logging.INFO)

        self.plugin_manager = plugins.PluginManager(
            plugin_dir=config["Plugins.Paths"]["plugindir"],
            base_dir=self.installdir if self.installdir is not None else os.path.dirname(__file__),
            signal=self.msg_signal,
            config=self.config,
            logger=pluginmgr_logger
        )
        self.loop_wait = int(self.config["Backend"]["loop_wait_ns"])
        self.pluginmain = config2bool(self.config["Plugins"]["enable_pluginmain"])

    def startup(self):
        # Initalize all plugins
        self.plugin_manager.load_plugins()
        self.plugin_manager.configure_plugins()
        self.msg_signal.emit("[CHAT WORKER | INFO] Dave From Seattle is READY!")

    def plugins_main(self):
        for name, _ in self.plugin_manager.plugins.items():
            t = time.time_ns()
            self.plugin_manager.plugin_run_function(name, "event_main", (t, self.loop_wait,))

    def message_notify(self, message):
        for name, _ in self.plugin_manager.plugins.items():
            self.plugin_manager.plugin_run_function(name, "event_message", (message))

    def run(self):
        """
        Starts the thread and continuously fetches messages from the chat.
        """
        self.startup()
        # While running, we fetch chat messages
        while self.running:
            self.usleep(self.loop_wait)
            if self.pluginmain: self.plugins_main()
            for c in self.chat.get().sync_items():
                # Process the message
                formatted_msg = convert_message(c, self.config)
                self.msg_signal.emit(formatted_msg)  # Update the GUI

                # Notify plugins
                self.message_notify(c)

    def stop(self):
        """
        Stop the chat fetching thread.
        """
        self.plugin_manager.unload_plugins()
        self.running = False

    def set_video_id(self, video_id: str):
        """
        Change the video ID and restart the chat.
        """
        self.video_id = video_id
        self.chat = pytchat.create(video_id=self.video_id)
