class PacketType(object):
    HELLO = 1
    ACK = 2
    NOACK = 3
    DATA = 4


class DeviceID(object):
    ULTRASOUND_FRONT = 1
    ULTRASOUND_LEFT = 2
    ULTRASOUND_RIGHT = 3
    ULTRASOUND_ARM_LEFT = 4
    ULTRASOUND_ARM_RIGHT = 5
    GYRO = 6


class Packet(object):
    def __init__(self, device_id, data):
        self.device_id = device_id
        self.data = data

    def _validate_checksum(self, checksum):
        return True

    @classmethod
    def deserialize(self, data):
        """Returns a list of packets that were serialized into the data."""
        return []

    @classmethod
    def get_packet_type(self, data):
        """Returns the packet type."""
        return PacketType.DATA
