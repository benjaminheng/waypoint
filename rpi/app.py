import time
from waypoint.utils.logger import get_logger
from waypoint.navigation.map import Map, Node
from waypoint.audio.text_to_speech import TextToSpeech
from waypoint.firmware.comms import Comms
from waypoint.firmware.packet import DeviceID
from waypoint.audio import constants as audio_text

logger = get_logger(__name__)


def prompt_for_path(nav_map):
    while True:
        speech.put(audio_text.SELECT_START_NODE)
        # TODO: get current node from keypad
        building1, level1, node1 = 'COM1', '2', '2'

        node_id1 = Node.get_node_id(building1, level1, node1)
        if nav_map.is_valid_node(node_id1):
            break
        speech.put(audio_text.INVALID_NODE.format(
            building1, level1, node1
        ))

    while True:
        speech.put(audio_text.SELECT_END_NODE)
        # TODO: get destination node
        building2, level2, node2 = 'COM2', '2', '10'
        node_id2 = Node.get_node_id(building2, level2, node2)
        if nav_map.is_valid_node(node_id2):
            break
        speech.put(audio_text.INVALID_NODE.format(
            building2, level2, node2
        ))

    speech.put(audio_text.SELECT_CONFIRMATION.format(
        building1, level1, node1,
        building2, level2, node2
    ))
    return node_id1, node_id2


if __name__ == '__main__':
    logger.info('Starting Waypoint')
    comms = Comms('/dev/ttyAMA0')
    comms.start()
    speech = TextToSpeech()
    speech.daemon = True
    speech.start()
    # TODO: get from cache if map fails to download
    nav_map = Map()

    start_node_id, end_node_id = prompt_for_path(nav_map)
    nav_map.search(start_node_id, end_node_id)

    # Set player position
    start_node = nav_map.path.pop(0)
    nav_map.next_node = nav_map.path.pop(0)
    nav_map.player.set_position(
        x=start_node.x,
        y=start_node.y,
        level=start_node.level,
        building=start_node.building,
    )

    # TODO: Get orientation data from packets
    nav_map.player.set_heading(90)

    # TODO: Orient user towards next node first
    turn = nav_map.calculate_player_turn_direction()
    logger.info('Initial orientation: {0}'.format(turn))

    while True:
        # packet = comms.device_queue.get(DeviceID.ULTRASOUND_FRONT).get()
        # logger.info(packet)
        time.sleep(1)
