import time
from collections import deque
from waypoint.utils.logger import get_logger
from waypoint.navigation.map import Map, Node
from waypoint.navigation.heading import (
    get_new_player_coordinates, get_turn_audio_text
)
from waypoint.audio.text_to_speech import TextToSpeech
from waypoint.firmware.comms import Comms
from waypoint.firmware.packet import DeviceID
from waypoint.firmware.keypad import wait_for_confirmed_input
from waypoint.audio import constants as audio_text
from waypoint.settings import (
    UF_FRONT_THRESHOLD, UF_LEFT_THRESHOLD, UF_RIGHT_THRESHOLD
)

logger = get_logger(__name__)
UF_HISTORY_LEN = 5

time_since_last_turn_speech = 0
time_since_last_obstacle_speech = 0

uf_count = {
    DeviceID.ULTRASOUND_FRONT: 0,
    DeviceID.ULTRASOUND_LEFT: 0,
    DeviceID.ULTRASOUND_RIGHT: 0,
}
uf_history = {
    DeviceID.ULTRASOUND_FRONT: deque(maxlen=UF_HISTORY_LEN),
    DeviceID.ULTRASOUND_LEFT: deque(maxlen=UF_HISTORY_LEN),
    DeviceID.ULTRASOUND_RIGHT: deque(maxlen=UF_HISTORY_LEN),

}

# If player has been told to stop
is_stopped = False


def get_uf_values():
    global uf_count
    global uf_history
    if all(uf_count[i] >= 5 for i in uf_count):
        for key in uf_count:
            uf_count[key] = 0
        middle = UF_HISTORY_LEN/2
        # Returns the "median" (does not account for even numbers)
        return (
            sorted(uf_history.get(DeviceID.ULTRASOUND_FRONT))[middle],
            sorted(uf_history.get(DeviceID.ULTRASOUND_LEFT))[middle],
            sorted(uf_history.get(DeviceID.ULTRASOUND_RIGHT))[middle],
        )
    else:
        return None, None, None


def put_uf_value(device_id, value):
    global uf_count
    global uf_history
    uf_history.get(device_id).append(value)
    uf_count[device_id] = uf_count.get(device_id) + 1


def prompt_for_path(nav_map):
    while True:
        speech.put(audio_text.SELECT_START_NODE)
        # get current node from keypad
        building1 = wait_for_confirmed_input()
        building1 = '{0}'.format(building1)
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
        building2 = '{0}'.format(building2)
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


def send_obstacle_speech(speech):
    global time_since_last_obstacle_speech
    if time.time() - time_since_last_turn_speech > 2:
        logger.info('Obstacle detected')
        speech.clear_with_content(audio_text.OBSTACLE_DETECTED)
        # speech.clear_queue()
        speech.put(audio_text.OBSTACLE_DETECTED)
        time_since_last_obstacle_speech = time.time()


def send_turn_speech(speech, direction, angle):
    global time_since_last_turn_speech
    # 2 seconds since last speech
    if time.time() - time_since_last_turn_speech > 4:
        logger.info('Turn {0}, {1}'.format(direction, angle))
        text = get_turn_audio_text(direction, angle)
        if text:
            speech.put(text)
            time_since_last_turn_speech = time.time()


def read_uf_sensors(comms):
    uf_front = comms.get_packet(DeviceID.ULTRASOUND_FRONT)
    uf_left = comms.get_packet(DeviceID.ULTRASOUND_LEFT)
    uf_right = comms.get_packet(DeviceID.ULTRASOUND_RIGHT)
    if uf_front:
        put_uf_value(DeviceID.ULTRASOUND_FRONT, uf_front.data)
    if uf_left:
        put_uf_value(DeviceID.ULTRASOUND_LEFT, uf_left.data)
    if uf_right:
        put_uf_value(DeviceID.ULTRASOUND_RIGHT, uf_right.data)


def obstacle_avoidance(speech, nav_map, comms):
    while True:
        read_uf_sensors(comms)
        uf_front_value, uf_left_value, uf_right_value = get_uf_values()
        if (
            (uf_front_value and uf_front_value < UF_FRONT_THRESHOLD) or
            (uf_left_value and uf_left_value < UF_LEFT_THRESHOLD) or
            (uf_right_value and uf_right_value < UF_RIGHT_THRESHOLD)
        ):
            send_obstacle_speech(speech)
        elif uf_front_value and uf_left_value and uf_right_value:
            logger.info('Obstacle cleared.')
            speech.put(audio_text.OBSTACLE_CLEARED, 5)
            return
        else:
            continue


def reorient_player(speech, nav_map, comms):
    while not nav_map.is_player_facing_next_node():
        compass = comms.get_packet(DeviceID.COMPASS)
        if compass:
            nav_map.player.set_heading(compass.data)

        direction, angle = nav_map.calculate_player_turn_direction()
        send_turn_speech(speech, direction, angle)
    speech.put(audio_text.PROCEED_FORWARD)


if __name__ == '__main__':
    logger.info('Starting Waypoint')
    comms = Comms('/dev/ttyAMA0')
    comms.start()
    speech = TextToSpeech()
    speech.daemon = True
    speech.start()
    # TODO: get from cache if map fails to download
    nav_map = Map()
    logger.info(nav_map.nodes)

    # TODO: Verify that nodes are different
    start_node_id, end_node_id = prompt_for_path(nav_map)
    # start_node_id, end_node_id = '1_2_10', '1_2_14'
    logger.info('Getting optimal path for: {0}, {1}'.format(
        start_node_id, end_node_id
    ))
    nav_map.search(start_node_id, end_node_id)
    logger.info(nav_map.path)

    # TODO: validate path exists

    # Set player position
    start_node = nav_map.path.pop(0)
    nav_map.next_node = nav_map.path.pop(0)
    nav_map.player.set_position_to_node(start_node)
    nav_map.set_steps_to_next_node()
    logger.info('Initialized player position to: {}, {}, {}, {}'.format(
        nav_map.player.x,
        nav_map.player.y,
        nav_map.player.building,
        nav_map.player.level,
    ))

    # Initialize player heading
    while True:
        logger.info('Initializing player heading')
        compass = comms.get_packet(DeviceID.COMPASS)
        if compass:
            nav_map.player.set_heading(compass.data)
            break

    # Orient user towards next node first
    turn = nav_map.calculate_player_turn_direction()
    logger.info('Initial orientation: {0}'.format(turn))
    speech.put(audio_text.INITIAL_ORIENTATION)
    while not nav_map.is_player_facing_next_node():
        compass = comms.get_packet(DeviceID.COMPASS)
        if compass:
            # Update player heading
            nav_map.player.set_heading(compass.data)
        direction, angle = nav_map.calculate_player_turn_direction()
        send_turn_speech(speech, direction, angle)
    speech.clear_queue()
    logger.info('Player is now facing first node.')

    step_count = 0
    last_steps = 0
    steps_since_last_node = 0
    time_since_last_speech = 0

    # initialize step counter
    while True:
        logger.info('Initializing step counter')
        step_counter = comms.get_packet(DeviceID.STEP_COUNT)
        # Break on the first valid packet
        if step_counter:
            last_steps = step_counter.data
            break

    # speech.put(audio_text.PROCEED_FORWARD)
    speech.put(audio_text.PROCEED_FORWARD_STEPS.format(
        nav_map.steps_to_next_node
    ))
    while True:
        step_counter = comms.get_packet(DeviceID.STEP_COUNT)
        if step_counter and step_counter.data > last_steps:
            delta = step_counter.data - last_steps
            last_steps = step_counter.data
            step_count += delta
            steps_since_last_node += delta
            logger.debug('step_count = {0}; steps_since_last_node = {1}'
                         .format(step_count, steps_since_last_node))

            # Set new player x,y coordinates
            if delta > 0:
                new_x, new_y = get_new_player_coordinates(
                    nav_map.player, nav_map.next_node, delta
                )
                nav_map.player.set_position(new_x, new_y)
                logger.info('Player coordinates: {0}, {1}'.format(
                    new_x, new_y
                ))

            # Player is near the next node, set his position to it.
            if nav_map.is_player_near_next_node():
                building, level, node = nav_map.next_node.audio_components
                logger.info('----------------------------------------')
                logger.info((building, level, node))
                logger.info('Player is near next node.')
                speech.put(audio_text.STOP, 1)
                is_stopped = True
                speech.put(audio_text.CURRENT_POSITION.format(
                    building, level, node
                ), 1)
                nav_map.player.set_position_to_node(nav_map.next_node)
                if len(nav_map.path) == 0:
                    speech.put(audio_text.STOP, 1)
                    speech.put(audio_text.DESTINATION_REACHED, 1)
                    speech.put(audio_text.YOU_ARE_THE_BEST, 1)
                    logger.info('Destination reached!')
                    # TODO: prompt for new path
                else:
                    nav_map.next_node = nav_map.path.pop(0)

                # Check if player needs to be reoriented after reaching node
                reorient_player(speech, nav_map, comms)
                # Reset step count between nodes
                steps_since_last_node = 0
                is_stopped = False

        compass = comms.get_packet(DeviceID.COMPASS)
        if compass:
            nav_map.player.set_heading(compass.data)
            if not is_stopped and not nav_map.is_player_facing_next_node():
                speech.put(audio_text.STOP, 1)
                is_stopped = True
                # This is a blocking call
                reorient_player(speech, nav_map, comms)
                is_stopped = False

        # TODO: add prompts when sensor is lost
        # Ultrasonic sensors
        read_uf_sensors(comms)
        uf_front_value, uf_left_value, uf_right_value = get_uf_values()
        if (
            (uf_front_value and uf_front_value < UF_FRONT_THRESHOLD) or
            (uf_left_value and uf_left_value < UF_LEFT_THRESHOLD) or
            (uf_right_value and uf_right_value < UF_RIGHT_THRESHOLD)
        ):
            send_obstacle_speech(speech)
            # Obstacle avoidance routine. This will unblock when cleared
            logger.info('Obstacle detected. Entering obstacle avoidance.')
            obstacle_avoidance(speech, nav_map, comms)
            speech.clear_with_content(audio_text.OBSTACLE_DETECTED)

            # TODO: reorient player?

            # Update step counter to ignore steps during avoidance
            while True:
                logger.info('Updating step counter after obstacle avoidance')
                step_counter = comms.get_packet(DeviceID.STEP_COUNT)
                # Break on the first valid packet
                if step_counter:
                    last_steps = step_counter.data
                    logger.debug('New last_steps: {0}'.format(last_steps))
                    break
