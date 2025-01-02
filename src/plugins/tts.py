from plugins import PluginInterface  # Assuming PluginInterface is defined in plugin_interface.py
import pyttsx3

class ExamplePlugin(PluginInterface):
    def event_load(self):
        print("TTS plugin loaded!")
        self.tts_engine = pyttsx3.init()
        self.prefix = "tts"  # Defalt config

    def event_message(self, m):
        # NO SPAM FILTER!
        if m.message.startswith(self.prefix):
            self.tts_engine.say(m.message)
    
    def event_kill(self):
        print("TTS plugin quit!")
        del self.tts_engine

    def configure(self, config):
        self.prefix = config["prefix"]