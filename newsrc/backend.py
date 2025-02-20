import processor
import fetcher
import sys
import multiprocessing

def setup():
    # Set up queue
    queue = multiprocessing.Queue()

    # Set up fetcher
    fetch = fetcher.CoreFetcher()
    fetch.livechat_connect("https://www.youtube.com/watch?v=jfKfPfyJRdk")

    # Set up processor
    proc = processor.CoreProcessor(queue, fetch)

    # Start the process
    prochost = multiprocessing.Process(target=proc.start)
    prochost.run()

    prochost.join()

if __name__ == "__main__":
    setup()