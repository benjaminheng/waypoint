import os
from threading import Thread
from Queue import PriorityQueue

COMMAND = 'flite -t "{0}"'


class TextToSpeech(Thread):
    def __init__(self):
        super(TextToSpeech, self).__init__()
        self.queue = PriorityQueue()

    def put(self, text, priority=10):
        self.queue.put((priority, text,))

    def run(self):
        while True:
            _, text = self.queue.get()
            os.system(COMMAND.format(text))
