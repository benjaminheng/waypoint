import time
from waypoint.utils.logger import get_logger
from waypoint.navigation.map import Map
from waypoint.audio.text_to_speech import TextToSpeech
from waypoint.firmware.comms import Comms
from waypoint.firmware.packet import DeviceID
from waypoint.audio.constants import (
    SELECT_START_NODE, SELECT_END_NODE,
    SELECT_CONFIRMATION,
    TURN_LEFT, TURN_RIGHT
)

logger = get_logger(__name__)


if __name__ == '__main__':
    logger.info('Starting Waypoint')
    comms = Comms('/dev/ttyAMA0')
    comms.start()
    speech = TextToSpeech()
    speech.start()

    speech.put(SELECT_START_NODE)
    # TODO: get current node from keypad
    building1, level1, node1 = 'COM 1', '1', '2'
    speech.put(SELECT_END_NODE)
    # TODO: get destination node
    building2, level2, node2 = 'COM 2', '2', '10'
    speech.put(SELECT_CONFIRMATION.format(
        building1, level1, node1,
        building2, level2, node2
    ))
    nav_map = Map()

    while True:
        packet = comms.device_queue.get(DeviceID.ULTRASOUND_FRONT).get()
        logger.info(packet)
        time.sleep(1)
