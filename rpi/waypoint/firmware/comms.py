import time
import serial
import io
from collections import deque
from threading import Thread
from waypoint.utils.logger import get_logger
from waypoint.firmware.packet import Packet, PacketType, DeviceID

logger = get_logger(__name__)


class UART(object):
    def __init__(self, port, **kwargs):
        self.s = serial.Serial(port, **kwargs)
        self.serial = io.TextIOWrapper(
            io.BufferedRWPair(self.s, self.s, 64),
            encoding='unicode-escape', newline='\x0D\x0A'
        )

    def read(self):
        self.s.flushInput()
        data = self.serial.readline()
        packet_type = Packet.get_packet_type(data)
        data = data.encode('raw_unicode_escape')
        return packet_type, data


class Comms(Thread):
    def __init__(self, uart_device, baudrate=115200,
                 timeout=None, **kwargs):
        super(Comms, self).__init__()
        self.last_received = time.time()
        self.is_dead = False
        self.dead_callback = None
        self.device_queue = {
            DeviceID.ULTRASOUND_FRONT: deque(maxlen=5),
            DeviceID.ULTRASOUND_LEFT: deque(maxlen=5),
            DeviceID.ULTRASOUND_RIGHT: deque(maxlen=5),
            DeviceID.KALMAN_FILTER: deque(maxlen=5),
            DeviceID.STEP_COUNT: deque(maxlen=1),
            DeviceID.COMPASS: deque(maxlen=5),
            DeviceID.INFRARED: deque(maxlen=5),
        }
        self.uart = UART(
            uart_device,
            baudrate=baudrate,
            timeout=timeout,
            **kwargs
        )

    def get_packet(self, device):
        if device in self.device_queue:
            try:
                return self.device_queue.get(device).popleft()
            except:
                return None
        return None

    def register_dead_callback(self, func):
        self.dead_callback = func

    def run(self):
        """Communication protocol implemented as a thread.

        Populates queue with packets received, which can be retrieved
        from the main thread.
        """
        callback_called = False
        while True:
            try:
                packet_type, data = self.uart.read()
                is_packet_valid = Packet.validate_checksum(data)
                if is_packet_valid:
                    if packet_type == PacketType.DATA:
                        packets = Packet.deserialize(data)
                        for packet in packets:
                            self.device_queue[packet.device_id].append(packet)

                        # Call callback ONCE if dead.
                        self.is_dead = (time.time() - self.last_received) > 1.5
                        self.last_received = time.time()
                        if (
                            self.is_dead and
                            self.dead_callback and
                            not callback_called
                        ):
                            self.dead_callback()
                            callback_called = True
                        if callback_called and not self.is_dead:
                            callback_called = False
                        logger.debug(
                            '\t'.join(
                                '{0}, {1}'.format(p.device_id, p.data)
                                for p in packets
                            )
                        )
            except Exception as e:
                logger.warning('{0}: {1}'.format(type(e).__name__, e))
