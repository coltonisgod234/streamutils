'''
This module connects all the other modules together
'''

import plugins
import fetcher
import processor
import multiprocessing

def setup():
    fetcher = fetcher.CoreFetcher()

    processor_queue = multiprocessing.Queue()
    processor = processor.CoreProcessor(processor_queue, fetcher)

    print("Starting processor...")
    processor.mpstart()

if __name__ == "__main__":
    setup()