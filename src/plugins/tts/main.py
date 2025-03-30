from pluginsdk import PluginInterface
import pyttsx3
import time

class TTSplugin(PluginInterface):
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def event_load(self, logger):
        self.engine = pyttsx3.init()

        self.logger = logger

    def event_message(self, m):
        self.logger.info("Got a message")

        # NO SPAM FILTER!
        if m.message.startswith(self.prefix):
            # self.tts_engine.say(m.message)
            self.logger.info("This is a TTS message")
            
            msg = m.message.replace(self.prefix, "", 1)
            self.speak(msg)
    
    def event_kill(self):
        self.logger.info("TTS plugin quit")
    
    def event_notify(self, source, data):
        return
    
    def event_main(self, time, loop_wait):
        return  # We don't care about what's going on this timeslice

    def configure(self, config):
        self.logger.info("Plugin configured")
        self.prefix = config["prefix"]
