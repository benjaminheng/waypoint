from __future__ import print_function

import sys
import pprint
from waypoint.utils.logger import get_logger
from waypoint.navigation.map import Map
from waypoint.firmware.comms import UART

"""Just a random debug module debug certain components.

Usage: python test.py name_of_function [...args]
"""

logger = get_logger(__name__)
pp = pprint.PrettyPrinter(indent=2)


def pretty_print(obj):
    pp.pprint(obj)


def print_nodes():
    """Print list of nodes"""
    nav_map = Map()
    print('North at: {0}'.format(nav_map.north_at))
    pretty_print(nav_map.nodes)


def print_graph_edges():
    """Print edges of graph"""
    nav_map = Map()
    pretty_print(nav_map.graph.edges)


def a_star_search(start='1_1', goal='1_7'):
    """Print edges of graph"""
    nav_map = Map()
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
    pretty_print(path)


def uart_receive(port):
    uart = UART(port)
    while True:
        packets = uart.read()
        print(packets)


def uart_send(port):
    uart = UART(port)
    while True:
        data = raw_input('Send data: ')  # NOQA
        uart.send(data)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in locals():
        locals()[sys.argv[1]](*sys.argv[2:])
    else:
        print('Usage: python test.py name_of_function [...args]')
