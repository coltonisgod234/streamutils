from plugins import PluginInterface
import pyttsx3

class TTSplugin(PluginInterface):
    def event_load(self):
        print("TTS plugin loaded!")
        self.tts_engine = pyttsx3.init()
        self.prefix = "tts"  # Defalt config

    def event_message(self, m):
        print("TTS plugin got a message.")
        # NO SPAM FILTER!
        if m.message.startswith(self.prefix):
            self.tts_engine.say(m.message)
    
    def event_kill(self):
        print("TTS plugin quit!")
        del self.tts_engine

    def configure(self, config):
        print(f"TTS plugin configured, config={config}")
        self.prefix = config["prefix"]
