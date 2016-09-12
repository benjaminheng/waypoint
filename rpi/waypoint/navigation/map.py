import requests
import heapq
from waypoint.settings import FLOORPLAN_URL, BUILDING_NAME
from waypoint.utils.logger import get_logger

logger = get_logger(__name__)


class Graph(object):
    """Graph representation of a map of nodes. Handles only node IDs."""
    def __init__(self):
        self.edges = {}

    def add_edge(self, from_node_id, to_node_id):
        self.edges.setdefault(from_node_id, [])
        self.edges[from_node_id].append(to_node_id)

    def neighbours(self, node_id):
        return self.edges[node_id]


class PriorityQueue(object):
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Node(object):
    """Describes a node on the map."""
    def __init__(self, node_id, x, y, name, adjacent_node_ids, level):
        node_id = '{0}_{1}'.format(level, node_id)
        adjacent = (
            '{0}_{1}'.format(level, i.strip())
            for i in adjacent_node_ids
        )
        self.id = node_id
        self.x = x
        self.y = y
        self.name = name
        self.adjacent = adjacent
        self.level = level

    def __str__(self):
        return '{0} {1} ({2}, {3})'.format(
            self.id, self.name, self.x, self.y
        )

    def __repr__(self):
        return self.__str__()


class Map(object):
    def __init__(self, building_name=BUILDING_NAME):
        self.levels = []
        self.nodes = {}
        self.graph = Graph()
        self.north_at = None
        self.wifi = {}
        self.download_floorplan(building_name)
        self.init_graph()

    def _has_more_levels(self, populated_levels, next_levels):
        """Does a SetB - SetA operation."""
        # NOTE: Can be optimized to used actual Set objects
        return len([i for i in next_levels if i not in populated_levels]) > 0

    def _parse_staircase_name(self, name):
        """Returns the levels a staircase links to."""
        levels = name.split('TO level')[-1].split(',')
        return (int(level) for level in levels)

    def _find_node_in_level(self, x, y, level):
        """Find a node with x and y coordinates in a given level."""
        for node_id in self.nodes:
            node = self.nodes.get(node_id)
            if node.level == level and node.x == x and node.y == y:
                return node

    def download_floorplan(self, building_name, level=1):
        """Recursively download floorplans for all building levels."""
        data = {
            'Building': building_name,
            'Level': level,
        }
        resp = requests.get(FLOORPLAN_URL, params=data)
        if resp.status_code != 200:
            return

        self.levels.append(level)
        result = resp.json()
        for point in result.get('map', {}):
            node = Node(
                point.get('nodeId'),
                int(point.get('x')),
                int(point.get('y')),
                point.get('nodeName'),
                [i.strip() for i in point.get('linkTo').split(',')],
                level
            )
            self.nodes[node.id] = node
            if node.name.startswith('TO level'):
                next_levels = self._parse_staircase_name(node.name)
        for i in next_levels:
            if i not in self.levels:
                self.download_floorplan(building_name, i)

    def init_graph(self):
        for node_id in self.nodes:
            node = self.nodes.get(node_id)
            for adjacent_node_id in node.adjacent:
                self.graph.add_edge(node.id, adjacent_node_id)
            # If node is a staircase, we add edges to corresponding nodes
            # on levels that the staircase links to.
            if node.name.startswith('TO level'):
                next_levels = self._parse_staircase_name(node.name)
                for level in next_levels:
                    next_node = self._find_node_in_level(node.x, node.y, level)
                    self.graph.add_edge(node.id, next_node.id)

    def heuristic(self, from_node_id, to_node_id):
        """Heuristic function used in A-star search algorithm.

        Calculates the distance between the current node and the goal node.
        Movement cost is used as a function for now. Heuristic may be tweaked
        if necessary.
        """
        return self.movement_cost(from_node_id, to_node_id)

    def movement_cost(self, from_node_id, to_node_id):
        """Function to calculate distance cost between two nodes."""
        from_node = self.nodes.get(from_node_id)
        to_node = self.nodes.get(to_node_id)
        return abs(from_node.x - to_node.x) + abs(from_node.y - to_node.y)

    def search(self, start, goal):
        """A-star search algorithm."""
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            for next in self.graph.neighbours(current):
                new_cost = (
                    cost_so_far[current] + self.movement_cost(current, next)
                )
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from, cost_so_far
