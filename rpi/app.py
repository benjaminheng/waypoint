import time
from waypoint.utils.logger import get_logger
from waypoint.navigation.map import Map, Node
from waypoint.audio.text_to_speech import TextToSpeech
from waypoint.firmware.comms import Comms
from waypoint.firmware.packet import DeviceID
from waypoint.firmware.keypad import wait_for_confirmed_input
from waypoint.audio import constants as audio_text
from waypoint.settings import STEP_LENGTH

logger = get_logger(__name__)


def prompt_for_path(nav_map):
    while True:
        speech.put(audio_text.SELECT_START_NODE)
        # get current node from keypad
        building1 = wait_for_confirmed_input()
        building1 = 'COM{0}'.format(building1)
        speech.put(building1)
        level1 = wait_for_confirmed_input()
        speech.put(level1)
        node1 = wait_for_confirmed_input()
        speech.put(node1)

        node_id1 = Node.get_node_id(building1, level1, node1)
        if nav_map.is_valid_node(node_id1):
            break
        speech.put(audio_text.INVALID_NODE.format(
            building1, level1, node1
        ))

    while True:
        speech.put(audio_text.SELECT_END_NODE)
        # get destination node
        building2 = wait_for_confirmed_input()
        building2 = 'COM{0}'.format(building2)
        speech.put(building2)
        level2 = wait_for_confirmed_input()
        speech.put(level2)
        node2 = wait_for_confirmed_input()
        speech.put(node2)

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

    # start_node_id, end_node_id = prompt_for_path(nav_map)
    start_node_id, end_node_id = 'COM1_2_2', 'COM2_2_10'
    logger.info('Getting optimal path for: {0}, {1}'.format(
        start_node_id, end_node_id
    ))
    nav_map.search(start_node_id, end_node_id)

    # Set player position
    start_node = nav_map.path.pop(0)
    nav_map.next_node = nav_map.path.pop(0)
    nav_map.player.set_position_to_node(start_node)

    # TODO: Get orientation data from packets
    nav_map.player.set_heading(90)

    # TODO: Orient user towards next node first
    turn = nav_map.calculate_player_turn_direction()
    logger.info('Initial orientation: {0}'.format(turn))

    step_count = 0
    last_step_counter = 0

    time_since_last_speech = 0

    while True:
        step_counter = comms.get_packet(DeviceID.STEP_COUNT)
        if step_counter > last_step_counter:
            delta = step_counter.data - last_step_counter
            last_step_counter = step_counter.data
            step_count += delta
            logger.debug('step_count = {0}'.format(step_count))
            # TODO: set new player x,y coordinates

            if nav_map.is_player_near_next_node():
                nav_map.player.set_position_to_node(nav_map.next_node)
                nav_map.next_node = nav_map.path.pop(0)

        # TODO: add prompts when sensor is lost
        uf_front = comms.get_packet(DeviceID.ULTRASOUND_FRONT)
        if uf_front:
            if uf_front.data < 100:
                if time.time() - time_since_last_speech > 2:
                    speech.put(audio_text.OBSTACLE_DETECTED)
                    time_since_last_speech = time.time()
            # logger.debug('uf_front.data = {0}'.format(uf_front.data))
