# chat_fetcher.py

import pytchat
# import emoji
from PyQt5.QtCore import QThread, pyqtSignal
import plugins
import emoji

import os
import importlib.resources
import emoji

# Stupid workaround for pyinstaller
language = "en"  # Change this at build time, screw you
with importlib.resources.path(emoji, f"unicode_codes/emoji_{language}.json") as path:
    emoji.EMOJI_DATA = path

import time

import logging

from dataclasses import dataclass

'''
Will be used later...
'''
@dataclass
class XAuthorContainer:
   platform:            str
   name:                str
   id
   url:                 str | None
   roles:               dict[str, bool]
   platform_specific:   dict
        
@dataclass
class XMessageContainer:
    platform:               str
                 
    # Cross platform stuff
    type:                   str
    id
    message:                str
    timestamp:              float
    datetime:               str | None
    dono_amount:            float | None
    dono_amount_string:     str
    dono_currency:          str
    dono_colour:            str
    author:                 XAuthorContainer

    # Platform specifics
    platform_specific:      dict

def convert_message_for_gui(c, config) -> tuple[str, str]:
    c.message = emoji.emojize(c.message)  # Sorry
    verbose = config["Frontend"].getboolean("verbose", False)

    if verbose:
        gui_message = f"\n\
            type={c.type}\n\
            id={c.id}\n\
            message={c.message}\n\
            messageEx={c.messageEx}\n\
            timestamp={c.timestamp}\n\
            datetime={c.datetime}\n\
            elapsedTime={c.elapsedTime}\n\
            donoAmountValue={c.amountValue}\n\
            donoAmountString={c.amountString}\n\
            donoCurrency={c.currency}\n\
            bgColour={c.bgColor}\n\
            author.name={c.author.name}\n\
            author.channelId={c.author.channelId}\n\
            author.channelUrl={c.author.channelUrl}\n\
            author.imageUrl={c.author.imageUrl}\n\
            author.badgeUrl={c.author.badgeUrl}\n\
            author.isVerified={c.author.isVerified}\n\
            author.isChatOwner={c.author.isChatOwner}\n\
            author.isChatModerator={c.author.isChatModerator}\n\
            author.isChatSponsor={c.author.isChatSponsor}"

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
        self.config = config

        self.running = True  # Flag to keep the thread running
        self.enablePlugins = config["Plugins"].getboolean("enable_plugins", False)
        self.installdir = config["Plugins.Paths"].get("installdir", None)

        self.logger = logging.getLogger("chatworker")
        self.logger.setLevel(logging.INFO)
        pluginmgr_logger = logging.getLogger("pluginmgr")
        pluginmgr_logger.setLevel(logging.INFO)

        if self.enablePlugins:
            self.plugin_manager = plugins.PluginManager(
                plugin_dir=config["Plugins.Paths"]["plugindir"],
                base_dir=self.installdir if self.installdir is not None else os.path.dirname(__file__),
                signal=self.msg_signal,
                config=self.config,
                logger=pluginmgr_logger
            )

        self.loop_wait = self.config["Backend"].getint("loop_wait_ns")
        self.pluginmain = self.config["Plugins"].getboolean("enable_pluginmain", False)

        self.set_video_id(self.video_id)

    def startup(self):
        # Initalize all plugins
        if self.enablePlugins:
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
                if not self.running:
                    self.logger.info("Running flipped from True to False, exiting...")
                    return

                formatted_msg = convert_message_for_gui(c, self.config)
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
        self.logger.info(f"Livestream URL set: {video_id}, restarting chat...")
        self.video_id = video_id
        self.chat = pytchat.create(video_id=self.video_id)
        self.logger.info(f"Restarted chat")
