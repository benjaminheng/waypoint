import os
from threading import Thread
from Queue import PriorityQueue

TTS_COMMAND = 'flite -voice rms -t "{0}"'
BEEP_COMMAND = 'play -n  synth 0.1 sin 347 2> /dev/null'


class TextToSpeech(Thread):
    def __init__(self):
        super(TextToSpeech, self).__init__()
        self.queue = PriorityQueue()

    def clear_with_content_startswith(self, content):
        with self.queue.mutex:
            self.queue.queue = [
                i for i in self.queue.queue
                if not i[1].lower().startswith(content.lower())
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
            os.system(TTS_COMMAND.format(text))


class ObstacleSpeech(Thread):
    def __init__(self):
        super(ObstacleSpeech, self).__init__()
        self.queue = PriorityQueue()

    def put(self, priority=10):
        self.queue.put((priority, 0.1))

    def clear_queue(self):
        with self.queue.mutex:
            # PriorityQueue uses a underlying list instead of a deque
            del self.queue.queue[:]

    def run(self):
        while True:
            _, text = self.queue.get()
            os.system(BEEP_COMMAND)
