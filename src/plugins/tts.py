from plugins import PluginInterface
import pyttsx3

class TTSplugin(PluginInterface):
    def event_load(self):
        print("TTS plugin loaded!")

    def event_message(self, m):
        print("TTS plugin got a message.")
        # NO SPAM FILTER!
        if m.message.startswith(self.prefix):
            # self.tts_engine.say(m.message)
            print("it's a TTS message!")
            msg = m.message.replace(self.prefix, "", 1)
            speak(msg)
    
    def event_kill(self):
        print("TTS plugin quit!")
        del self.tts_engine

    def configure(self, config):
        print(f"TTS plugin configured, config={config}")
        self.prefix = config["prefix"]

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
