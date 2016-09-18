from unittest import TestCase
from mock import patch, MagicMock
from waypoint.firmware.comms import UART
from waypoint.firmware.packet import Packet


class TestComms(TestCase):
    @patch('serial.Serial')
    @patch('io.TextIOWrapper')
    @patch('io.BufferedRWPair')
    def setUp(self, s, tio, brwp):
        self.uart = UART('/dev/ttyAMA0')
        self.uart.serial = MagicMock()

        self.packet_type = 0x03
        self.data1 = 0x101
        self.data2 = 0x202
        self.data3 = 0x303
        self.data = (
            '\x01' +
            '\x03' +
            '\x01\x01\x01' +
            '\x02\x02\x02' +
            '\x03\x03\x03' +
            '\x02'
        )

    def _set_data(self, data):
        self.uart.serial.readline = MagicMock(return_value=data)

    def test_checksum(self):
        is_valid = Packet.validate_checksum(self.data)
        self.assertTrue(is_valid)

    def test_deserialize(self):
        packets = Packet.deserialize(self.data)
        self.assertEquals(self.data1, packets[0].data)
        self.assertEquals(self.data2, packets[1].data)
        self.assertEquals(self.data3, packets[2].data)

    def test_uart_read(self):
        self._set_data(self.data)
        packet_type, read_data = self.uart.read()
        self.assertEquals(self.data[0], packet_type)
        self.assertEquals(self.data, read_data)
