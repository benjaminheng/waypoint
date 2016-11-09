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
        if data:
            try:
                packet_type = Packet.get_packet_type(data)
                data = data.encode('raw_unicode_escape')
                return packet_type, data
            except Exception as e:
                logger.warning('{0}:: {1}'.format(type(e).__name__, e))
        return (None, None)


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
                if packet_type is None:
                    continue
                if (
                    packet_type is None and
                    self.dead_callback is not None and
                    not self.is_dead
                ):
                    self.dead_callback()
                    callback_called = True
                    self.is_dead = True
                elif packet_type is not None:
                    self.is_dead = False
                if callback_called and not self.is_dead:
                    callback_called = False

                is_packet_valid = Packet.validate_checksum(data)
                if is_packet_valid:
                    if packet_type == PacketType.DATA:
                        packets = Packet.deserialize(data)
                        for packet in packets:
                            self.device_queue[packet.device_id].append(packet)
                        logger.debug(
                            '\t'.join(
                                '{0}, {1}'.format(p.device_id, p.data)
                                for p in packets
                            )
                        )
            except Exception as e:
                logger.warning('{0}: {1}'.format(type(e).__name__, e))
