"""Module for PID handler with DAC."""

import threading

class PidHandler(threading.Thread):
    """PID handler for configuring and running feedback control on WLM channels."""

    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        pass
