import math
from waypoint.settings import STEP_LENGTH
from waypoint.utils.logger import get_logger
from waypoint.audio import constants as audio_text

logger = get_logger(__name__)

CONE_THRESHOLD = 20


def get_turn_audio_text(turn_direction, turn_angle):
    if abs(turn_angle) > CONE_THRESHOLD and abs(turn_angle) < 80:
        return audio_text.TURN_SLIGHTLY.format(turn_direction)
    elif abs(turn_angle) > CONE_THRESHOLD and abs(turn_angle) >= 80:
        return audio_text.TURN.format(turn_direction)
    return None


def get_new_player_coordinates(player, to_node, steps):
    return get_new_coordinates(
        from_x=player.x,
        from_y=player.y,
        to_x=to_node.x,
        to_y=to_node.y,
        distance=steps * STEP_LENGTH
    )


def get_new_coordinates(from_x, from_y, to_x, to_y, distance):
    radians = math.atan2(to_y - from_y, to_x - from_x)
    degrees = math.degrees(radians)

    if 0 <= degrees <= 90:
        dx = distance * math.cos(radians)
        dy = distance * math.sin(radians)
    elif 90 < degrees <= 180:
        rad = math.radians(90 - (degrees - 90))
        dx = -(distance * math.cos(rad))
        dy = distance * math.sin(rad)
    elif -90 <= degrees < 0:
        dx = distance * math.cos(abs(radians))
        dy = distance * math.sin(radians)
    else:
        rad = math.radians(90 - (abs(degrees) - 90))
        dx = -(distance * math.cos(rad))
        dy = -(distance * math.sin(rad))
    logger.info(degrees)
    logger.info(distance)
    logger.info(from_x)
    logger.info(from_y)
    logger.info(dx)
    logger.info(dy)
    return from_x + dx, from_y + dy


def calculate_turn_direction(from_x, from_y, to_x, to_y, heading, north):
    degrees = math.degrees(math.atan2(
        to_y - from_y, to_x - from_x
    ))
    degrees = degrees % 360
    if degrees < 90:
        degrees = 90 - degrees
    else:
        degrees = degrees - 90
        degrees = 360 - degrees

    # Calculate offset between map north and true north
    map_north_offset = 360 - north

    # Normalize node direction with respect to true north
    # `degrees` now points to the next node
    degrees = map_north_offset + degrees
    if degrees > 360:
        degrees = abs(360 - degrees)

    # Slice compass in half
    offset = 180 if degrees < 180 else -180
    opposite_degrees = degrees + offset

    if (opposite_degrees < heading < degrees) or \
            (degrees < heading < opposite_degrees):
        if heading > degrees:
            return 'left', int(heading - degrees)
        else:
            return 'right', int(degrees - heading)
    else:
        difference = abs(heading - degrees)
        if difference > 180:
            if heading > opposite_degrees:
                turn_degrees = 180 - (heading - opposite_degrees)
            else:
                turn_degrees = 180 - (opposite_degrees - heading)
        else:
            if heading > degrees:
                turn_degrees = heading - degrees
            else:
                turn_degrees = degrees - heading

        if degrees > opposite_degrees:
            return 'left', int(turn_degrees)
        else:
            return 'right', int(turn_degrees)


def is_pointing_to_node(from_x, from_y, to_x, to_y, heading, north):
    degrees = math.degrees(math.atan2(
        to_y - from_y,
        to_x - from_x
    ))
    degrees = degrees % 360
    if degrees < 90:
        degrees = 90 - degrees
    else:
        degrees = degrees - 90
        degrees = 360 - degrees

    # Calculate offset between map north and true north
    map_north_offset = 360 - north

    # Normalize node direction with respect to true north
    # `degrees` now points to the next node
    degrees = map_north_offset + degrees
    if degrees > 360:
        degrees = abs(360 - degrees)

    # http://stackoverflow.com/questions/12234574/calculating-if-an-angle-is-between-two-angles
    diff = (heading - degrees + 180 + 360) % 360 - 180
    if diff <= CONE_THRESHOLD and diff >= -CONE_THRESHOLD:
        return True
    return False


def calculate_distance_between_nodes(from_x, from_y, to_x, to_y):
    return math.hypot(abs(to_x - from_x), abs(to_y - from_y))


def approximate_steps(distance):
    return distance / STEP_LENGTH
