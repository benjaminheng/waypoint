import time
import RPi.GPIO as GPIO
from threading import Thread
from waypoint.utils.logger import get_logger

logger = get_logger(__name__)

# Columns 1 - 3
COLUMNS = [16, 11, 13]
# Rows 1 - 4
ROWS = [15, 19, 21, 23]

KEY_MAP = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    ['*', 0, '#'],
]

GPIO.setmode(GPIO.BOARD)

for pin in COLUMNS:
    GPIO.setup(pin, GPIO.OUT)
for pin in ROWS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def wait_for_confirmed_input():
    inputs = []
    key = None
    while True:
        key = wait_for_input()
        if key == '#' and len(inputs) > 0:
            break
        inputs.append(key)
    return ''.join(str(i) for i in inputs)


def wait_for_input(timeout=None):
    """Wait for keypad input. Set timeout to None to disable."""
    key = None
    lastKey = None
    start = time.time()
    count = 0
    while True:
        key = get_input()
        if key is not None:
            lastKey = key
            count = 0
        elif lastKey is not None:
            count += 1
            if count > 10:
                return lastKey
        # Timeout
        if timeout is not None and time.time() - start > timeout:
            return None


def check_pins(*args):
    return all(not GPIO.input(i) for i in args)


def print_pins(*args):
    return [GPIO.input(i) for i in args]


def get_input():
    for column in COLUMNS:
        GPIO.output(column, GPIO.LOW)

    for i, column in enumerate(COLUMNS):
        GPIO.output(column, GPIO.HIGH)
        for j, row in enumerate(ROWS):
            if GPIO.input(row):
                try:
                    return KEY_MAP[j][i]
                except:
                    return None
        GPIO.output(column, GPIO.LOW)
    return None


class KeypadThread(Thread):
    def __init__(self):
        super(KeypadThread, self).__init__()
        self.callbacks = {}
        self.enable = False

    def register_callback(self, code, callback_func, args=[]):
        self.callbacks[code] = (callback_func, args,)

    def run(self):
        while True:
            try:
                if self.enable:
                    code = wait_for_confirmed_input()
                    if code in self.callbacks:
                        func, args = self.callbacks.get(code)
                        logger.info('Callback: {0}'.format(func))
                        func(*args)
                else:
                    time.sleep(1)
            except Exception as e:
                logger.warning('{0}: {1}'.format(type(e).__name__, e))
