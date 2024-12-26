"""
Holds callback functions for commands
"""
import pyttsx3
pyttsx3.init()

def tts(msg):
    """
    Does a text to speech message
    """
    msg = msg.strip("/tts")

    pyttsx3.speak(msg)

def handle_commands(msg):
    # Check for commands
    if msg.startswith("/tts"):
        tts(msg)