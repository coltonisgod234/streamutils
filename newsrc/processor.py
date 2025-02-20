import fetcher

class CoreProcessor:
    '''
    Processes chat messages from a CoreFetcher queue, translates them into events and
    sends them through a multiprocessing.Queue()
    '''
    def __init__(self, pipe, fetcher):
        self.fetcher = fetcher
        self.running = False
        self.queue = pipe
    
    def process_event(self):
        '''
        Processes the next event in the Queue
        '''
        event = self.queue.get()
        if event.startswith("TERMINATE;"):
            print("[CoreProcessor] GOT TERMINATE EVENT. QUITTING...")
            self.stop()

    def next_message(self):
        '''
        Proceses the next message and generates an event
        '''
        self.fetcher.queue_next()

        message = self.fetcher.queue_process()
        self.queue.put(f"MESSAGE;{message.stringified}")
        self.queue.put(f"MESSAGESERIAL;")
        self.queue.put(message)

    def stop(self):
        '''
        Terminate the thread
        '''
        self.running = False
    
    def start(self):
        '''
        Begin the thread, usually a target for multiprocessing.Process()
        '''
        self.running = True
        while self.running:
            self.next_message()
