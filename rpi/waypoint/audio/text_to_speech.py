import os
from threading import Thread
from Queue import PriorityQueue

TTS_COMMAND = 'flite -voice rms -t "{0}"'

BEEP_LEFT_COMMAND = 'play /home/pi/waypoint/rpi/beeps/beepleft.wav 2> /dev/null'  # NOQA
BEEP_RIGHT_COMMAND = 'play /home/pi/waypoint/rpi/beeps/beepright.wav 2> /dev/null'  # NOQA
BEEP_COMMAND = 'play /home/pi/waypoint/rpi/beeps/beepboth.wav 2> /dev/null'


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

    def put(self, side, priority=10):
        self.queue.put((priority, side))

    def clear_queue(self):
        with self.queue.mutex:
            # PriorityQueue uses a underlying list instead of a deque
            del self.queue.queue[:]

    def run(self):
        while True:
            _, side = self.queue.get()
            if side == 'front':
                os.system(BEEP_COMMAND)
            elif side == 'right':
                os.system(BEEP_RIGHT_COMMAND)
            elif side == 'left':
                os.system(BEEP_LEFT_COMMAND)
