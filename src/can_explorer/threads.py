import threading


class StoppableThread(threading.Thread):
    """
    Basic thread that creates an event which can be implemented
    in the run method to interrupt long running loops.

    Example:
        def run(self):
            while not self.cancel.wait(5):
                ...
    """

    def __init__(self, daemon=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = daemon
        self.cancel = threading.Event()

    def stop(self):
        self.cancel.set()
        self.join()
