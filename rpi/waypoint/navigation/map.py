import requests
import heapq
from waypoint.settings import FLOORPLAN_URL, BUILDING_NAME
from waypoint.utils.logger import get_logger

logger = get_logger(__name__)


class Graph(object):
    def __init__(self):
        self.edges = {}

    def add_edge(self, from_node, to_node):
        self.edges[from_node.id] = to_node

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

    def _has_more_levels(self, populated_levels, next_levels):
        return len([i for i in next_levels if i not in populated_levels]) > 0

    def download_floorplan(self, building_name, level=1):
        """Recursively download floorplans for all building levels."""
        next_levels = []
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
                point.get('x'),
                point.get('y'),
                point.get('nodeName'),
                [i.strip() for i in point.get('linkTo').split(',')],
                level
            )
            self.nodes[node.id] = node
            if node.name.startswith('TO level'):
                next_levels.extend(
                    int(level) for level in
                    node.name.split('TO level')[-1].split(',')
                )
        for i in next_levels:
            if i not in self.levels:
                self.download_floorplan(building_name, i)

    def heuristic(self, node1, node2):
        return abs(node1.x - node2.x) + abs(node1.y - node2.y)

    def search(self, start, goal):
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

            for next in self.graph.neighbors(current):
                new_cost = (
                    cost_so_far[current] + self.graph.cost(current, next)
                )
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from, cost_so_far
