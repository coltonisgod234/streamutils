import pytchat
import sys
import time

class ProcessedMessage:
    def __init__(self, msg, string):
        self.stringified = string
        self.message = msg
    
    def __repr__(self):
        m = self.message
        return m.__repr__()

class CoreFetcher:
    '''
    Fetches chat messages and maintains a queue to process them
    '''
    def __init__(self):
        self.chat = None
        self.message_queue = []
    
    def livechat_connect(self, video):
        '''
        Connects the program to a given livechat
        '''
        self.chat = pytchat.create(video)
    
    def livechat_disconnect(self):
        '''
        Disconnects from the chat
        '''
        self.chat = None

    def queue_next(self):
        '''
        Gets the next message(s) from the chat and adds it to the queue for processing
        '''
        for msg in self.chat.get().sync_items():
            self.message_queue.append(msg)

    def queue_process(self):
        '''
        Returns the current message and removes it from the queue
        '''
        try:
            message = self.message_queue.pop()
            return ProcessedMessage(message, f"[{message.author.name}]: {message.message}\n")
        except IndexError:
            return ProcessedMessage(None, "")
