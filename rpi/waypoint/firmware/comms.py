import serial
import io
from Queue import LifoQueue
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
        self.device_queue = {
            DeviceID.ULTRASOUND_FRONT: LifoQueue(),
            DeviceID.ULTRASOUND_LEFT: LifoQueue(),
            DeviceID.ULTRASOUND_RIGHT: LifoQueue(),
            DeviceID.KALMAN_FILTER: LifoQueue(),
            DeviceID.STEP_COUNT: LifoQueue(),
            DeviceID.COMPASS: LifoQueue(),
        }
        self.uart = UART(
            uart_device,
            baudrate=baudrate,
            timeout=timeout,
            **kwargs
        )

    def run(self):
        """Communication protocol implemented as a thread.

        Populates queue with packets received, which can be retrieved
        from the main thread.
        """
        while True:
            try:
                packet_type, data = self.uart.read()
                is_packet_valid = Packet.validate_checksum(data)
                if is_packet_valid:
                    if packet_type == PacketType.DATA:
                        packets = Packet.deserialize(data)
                        for packet in packets:
                            self.device_queue[packet.device_id].put(packet)
                        logger.debug(
                            '\t'.join(
                                '{0}, {1}'.format(p.device_id, p.data)
                                for p in packets
                            )
                        )
            except Exception as e:
                logger.warning('{0}: {1}'.format(type(e).__name__, e))
