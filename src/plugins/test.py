import sys

def run(message_queue, event_queue, config: dict):
    '''
    This method runs in a thread upon the plugins startup.

    Arguments
    ---------
    message_queue:
        Any argument named `message_queue` will be given an asyncio.Queue object
        to send pytchat message objects to the client

    event_queue:
        Any argument named `event_queue` will be given an asyncio.Queue object
        to communicate with the host
    '''
    sys.stdout.write("Heyy!")
    sys.stdout.flush()
    messages = message_queue
    events = event_queue
    print("[Example] Plugin started!")