import serial
import io
from threading import Thread
from waypoint.firmware.packet import Packet


class UART(object):
    def __init__(self, port, **kwargs):
        ser = serial.Serial(port, **kwargs)
        # Recommended. Remove wrapper if problematic.
        self.serial = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

    def read(self):
        data = self.serial.readline()
        packet_type = Packet.get_packet_type(data)
        return packet_type, data

    def write(self, device_id, data):
        pass


class Comms(Thread):
    def __init__(self, uart_device, queue, baudrate=115200,
                 timeout=5, **kwargs):
        self.queue = queue
        self.uart = UART(
            uart_device,
            baudrate=baudrate,
            timeou=timeout,
            **kwargs
        )

    def run(self):
        """Communication protocol implemented as a thread.

        Populates queue with packets received, which can be retrieved
        from the main thread.
        """
        pass
