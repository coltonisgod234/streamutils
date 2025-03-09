from pluginsdk import PluginInterface
import pyttsx3

class TTSplugin(PluginInterface):
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def event_load(self):
        self.engine = pyttsx3.init()

        self.log(self.LINFO, "TTS plugin loaded!")

    def event_message(self, m):
        self.log(self.LINFO, "TTS plugin got a message.")

        # NO SPAM FILTER!
        if m.message.startswith(self.prefix):
            # self.tts_engine.say(m.message)
            self.log(self.LINFO, "it's a TTS message!")
            
            msg = m.message.replace(self.prefix, "", 1)
            self.speak(msg)
    
    def event_kill(self):
        self.log(self.LINFO, "TTS plugin quit!")
        del self.engine
    
    def event_notify(self, source, data):
        return
    
    def event_main(self, time, loop_wait):
        return  # We don't care about what's going on this timeslice

    def configure(self, config):
        self.log(self.LINFO, f"TTS plugin configured, config={config}")
        self.prefix = config["prefix"]
