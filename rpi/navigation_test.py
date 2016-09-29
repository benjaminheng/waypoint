from __future__ import print_function

import pprint
import math
from waypoint.navigation.map import Map

"""Demonstration application for the Week 7 Prototype evaluation (software)."""


MENU = (
    '1. Path finding\n'
    '2. Directions'
)


def pretty_print(obj):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(obj)


def find_path(nav_map, start='1_1', goal='1_7'):
    """Print edges of graph"""
    came_from, _ = nav_map.search(start, goal)
    # Print path taken
    current = goal
    current_node = nav_map.nodes.get(current)
    path = [current_node]
    while current != start:
        current = came_from[current]
        current_node = nav_map.nodes.get(current)
        path.append(current_node)
    path.reverse()
    return path


if __name__ == '__main__':
    building = raw_input('Building Name: ')  # NOQA
    level = input('Level: ')
    nav_map = Map(building, level)
    print('North at: {0}'.format(nav_map.north_at))
    pretty_print(nav_map.nodes)

    option = ''
    while option != 'exit':
        print(MENU)
        option = raw_input('> ')  # NOQA

        if option == '1':
            option = raw_input('Start, End node: ')  # NOQA
            while option != 'exit':
                start, end = [i.strip() for i in option.split(',')]
                path = find_path(nav_map, start, end)
                pretty_print(path)
                option = raw_input('Start, End node: ')  # NOQA
        else:
            option = raw_input('Start, End node: ')  # NOQA
            while option != 'exit':
                start, end = [i.strip() for i in option.split(',')]
                path = find_path(nav_map, start, end)

                option = raw_input('x, y, heading: ')  # NOQA
                while option != 'exit':
                    x, y, heading = [int(i.strip()) for i in option.split(',')]
                    nearest_node = None
                    lowest_cost = None
                    # Iterate from back, in case two nodes have same cost.
                    for node in path[::-1]:
                        cost = abs(x - node.x) + abs(y - node.y)
                        if lowest_cost is None or cost < lowest_cost:
                            lowest_cost = cost
                            nearest_node = node
                    north = nav_map.north_at

                    # Get the direction of the nearest node
                    if north == 90:
                        # east
                        degrees = math.degrees(math.atan2(
                            nearest_node.y - y, nearest_node.x - x
                        ))
                    elif north == 0:
                        # north
                        degrees = math.degrees(math.atan2(
                            x - nearest_node.x, nearest_node.y - y
                        ))
                    elif north == 180:
                        # south
                        degrees = math.degrees(math.atan2(
                            nearest_node.x - x, y - nearest_node.y
                        ))
                    elif north == 270:
                        # west
                        degrees = math.degrees(math.atan2(
                            y - nearest_node.y, x - nearest_node.x
                        ))
                    # right turn: +ve, left turn: -ve
                    degrees = -degrees
                    # normalize node direction with respect to north
                    norm_deg = degrees
                    if degrees <= 0:
                        norm_deg = 360 - abs(degrees)
                    # Get the opposite direction from the node
                    deg_range = (
                        norm_deg - 180
                        if norm_deg > 180 else norm_deg + 180
                    )

                    # identify the lower and upper directions
                    lower, upper = (
                        (deg_range, norm_deg)
                        if deg_range < norm_deg
                        else (norm_deg, deg_range)
                    )

                    # if heading falls between lower and upper bound,
                    # we can easily figure out the direction to turn
                    if lower < heading < upper:
                        if heading < norm_deg:
                            result = abs(norm_deg - heading)
                        else:
                            result = -abs(heading - norm_deg)
                    # turn left if node is to our left and less than 90deg
                    elif upper == norm_deg and heading > upper and \
                            heading - upper <= 90:
                        result = -abs(heading - norm_deg)
                    # turn right if node is to our right less than 90deg
                    elif lower == norm_deg and heading < lower and \
                            lower - heading <= 90:
                        result = abs(norm_deg - heading)
                    # edge case where the node is on the opposite side of north
                    # boundary (ie. the transition between 360deg and 0deg)
                    elif upper == norm_deg:
                        result = -abs(360 - upper + heading)
                    # similar edge case to the above, but in opposite direction
                    else:
                        result = abs(360 - heading + lower)

                    # right turn: +ve, left turn: -ve
                    # degrees = -degrees
                    distance = math.hypot(
                        nearest_node.x - x, nearest_node.y - y
                    )
                    print(nearest_node)
                    print('Turning angle: {0}'.format(result))
                    print('Distance: {0}'.format(distance))
                    option = raw_input('x, y, heading: ')  # NOQA
