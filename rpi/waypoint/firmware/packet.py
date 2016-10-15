import struct
"""
Packet format:
PACKET_TYPE (1byte)
NUM_DEVICES (1byte)
PAYLOAD (per device)
DEVICE_ID (1byte)
DATA (2bytes)
"""


class PacketType(object):
    HELLO = 1
    ACK = 2
    NACK = 3
    DATA = 4


class DeviceID(object):
    ULTRASOUND_FRONT = 1
    ULTRASOUND_LEFT = 2
    ULTRASOUND_RIGHT = 3
    KALMAN_FILTER = 4
    STEP_COUNT = 5
    COMPASS = 6


class Packet(object):
    def __init__(self, device_id, data):
        self.device_id = device_id
        self.data = data

    @classmethod
    def validate_checksum(self, buf):
        values = [
            int(i.encode('hex'), 16)
            for i in buf
        ]
        checksum = 0
        for i in values[:-3]:
            checksum ^= i
        return values[-3] == checksum

    @classmethod
    def deserialize(self, data):
        """Returns a list of packets that were serialized into the data."""
        # 1. Unpack header to determine packet type and number of devices
        # 2. Unpack number of devices, assuming each is a fixed length
        # 3. Serialize packets and return a list of them

        packets = []
        packet_type, num_devices = struct.unpack('cc', data[:2])
        num_devices = int(num_devices.encode('hex'), 16)

        fmt = ''.join('3s' * num_devices)
        devices = struct.unpack(fmt, data[2:-3])

        for device in devices:
            device_id = int(device[0].encode('hex'), 16)
            device = device[::-1]
            device_data = int(device[:2].encode('hex'), 16)
            packet = Packet(device_id, device_data)
            packets.append(packet)
        return packets

    @classmethod
    def get_packet_type(self, data):
        """Returns the packet type."""
        return int(data[0].encode('hex'), 16)
