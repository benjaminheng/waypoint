import serial
import time
import io
from Queue import Queue
from threading import Thread
from waypoint.firmware.packet import Packet, PacketType, DeviceID


class UART(object):
    def __init__(self, port, **kwargs):
        self.s = serial.Serial(port, **kwargs)
        self.serial = io.TextIOWrapper(io.BufferedRWPair(self.s, self.s, 64), encoding = 'unicode-escape', newline='\x0D\x0A')

    def read(self):
        self.s.flushInput()
        data = self.serial.readline()
        packet_type = Packet.get_packet_type(data)
        data = data.encode('raw_unicode_escape')
        return packet_type, data

    def write(self):
        self.serial.write(u'A')


class Comms(Thread):
    def __init__(self, uart_device, baudrate=115200,
                 timeout=None, **kwargs):
        self.device_queue = {
            DeviceID.ULTRASOUND_FRONT: Queue(),
            DeviceID.ULTRASOUND_LEFT: Queue(),
            DeviceID.ULTRASOUND_RIGHT: Queue(),
            DeviceID.KALMAN_FILTER: Queue(),
            DeviceID.STEP_COUNT: Queue(),
            DeviceID.COMPASS: Queue(),
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
        # Populate device data like this
        while True:
            try:
                pkttype, data = self.uart.read()
                pkt_no_error = Packet.validate_checksum(data)
                if pkt_no_error:
                    #print('checksum passed')
                    if int(pkttype.encode('hex'), 16) == PacketType.DATA:
                        #print('packet type is data')
                        packets = Packet.deserialize(data)
                        for packet in packets:
                            self.device_queue[packet.device_id].put(packet)
                            pkt = self.device_queue[packet.device_id].get()
                        print('\t'.join('{0}, {1}'.format(p.device_id, p.data) for p in packets))
            except:
                pass
                        
