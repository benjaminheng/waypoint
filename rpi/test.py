from __future__ import print_function

import sys
import pprint
from waypoint.utils.logger import get_logger
from waypoint.navigation.map import Map

"""Just a test module to test certain components.

Usage: python test.py name_of_function [...args]
"""

logger = get_logger(__name__)
pp = pprint.PrettyPrinter(indent=2)


def pretty_print(obj):
    pp.pprint(obj)

def print_nodes():
    """Print list of nodes"""
    nav_map = Map()
    pretty_print(nav_map.nodes)

def print_graph_edges():
    """Print edges of graph"""
    nav_map = Map()
    pretty_print(nav_map.graph.edges)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in locals():
        locals()[sys.argv[1]](*sys.argv[2:])
    else:
        print('Usage: python test.py name_of_function [...args]')
