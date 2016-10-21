import os
from threading import Thread
from Queue import PriorityQueue

COMMAND = 'flite -voice rms -t "{0}"'


class TextToSpeech(Thread):
    def __init__(self):
        super(TextToSpeech, self).__init__()
        self.queue = PriorityQueue()

    def clear_with_content_startswith(self, content):
        with self.queue.mutex:
            self.queue.queue = [
                i for i in self.queue.queue if not i[1].startswith(content)
            ]

    def clear_with_content(self, content):
        with self.queue.mutex:
            self.queue.queue = [i for i in self.queue.queue if i[1] != content]

    def clear_queue(self):
        with self.queue.mutex:
            # PriorityQueue uses a underlying list instead of a deque
            del self.queue.queue[:]

    def put(self, text, priority=10):
        self.queue.put((priority, text,))

    def run(self):
        while True:
            _, text = self.queue.get()
            os.system(COMMAND.format(text))
