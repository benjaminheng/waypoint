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
    # building = raw_input('Building Name: ')  # NOQA
    # level = input('Level: ')
    building = 'DemoBuilding'
    level = 1
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
                    # dy = nearest_node.y - y
                    # dx = nearest_node.x - x
                    # degrees = math.degrees(math.atan2(dy, dx))
                    print(nearest_node)
                    option = raw_input('x, y, heading: ')  # NOQA
