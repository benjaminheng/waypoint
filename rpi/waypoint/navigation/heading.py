import math


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
            return 'left', heading - degrees
        else:
            return 'right', degrees - heading
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
            return 'left', turn_degrees
        else:
            return 'right', turn_degrees
