import json
import math
import requests
import heapq
import re
from waypoint.settings import (
    FLOORPLAN_URL, BUILDINGS, NODE_PROXIMITY_THRESHOLD, STEP_LENGTH,
    CACHE_FILE
)
from waypoint.navigation.heading import (
    calculate_turn_direction, is_pointing_to_node
)
from waypoint.utils.logger import get_logger

LINK_RE = re.compile('TO (?P<building>\w+)-(?P<level>\d+)-(?P<node>\d+)')
BUILDING_RE = re.compile('(?P<building>COM)(?P<building_id>\d+)')

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
    def __init__(self, node_id, x, y, name, adjacent_node_ids, level,
                 building):
        node_id = self._get_node_id(building, level, node_id)
        adjacent = (
            self._get_node_id(building, level, i.strip())
            for i in adjacent_node_ids
        )
        self.id = node_id
        self.x = x
        self.y = y
        self.name = name
        self.adjacent = adjacent
        self.level = level
        self.building = building

    @property
    def components(self):
        """Returns the building, level, and ID of the node for speech."""
        return self.id.split('_')

    @property
    def audio_components(self):
        building, level, node = self.components
        # try:
        #     match = BUILDING_RE.match(building)
        #     building_name = match.group('building')
        #     building_id = match.group('building_id')
        #     building = '{0}, {1}'.format(building_name, building_id)
        # except:
        #     pass
        return building, level, node

    @classmethod
    def get_node_id(self, building, level, node_id):
        return '{0}_{1}_{2}'.format(building, level, node_id)

    def _get_node_id(self, building, level, node_id):
        return '{0}_{1}_{2}'.format(building, level, node_id)

    def __str__(self):
        return '{0} {1} ({2}, {3})'.format(
            self.id, self.name, self.x, self.y
        )

    def __repr__(self):
        return self.__str__()


class PlayerNode(Node):
    def __init__(self):
        self.heading = None
        self.id = 'PLAYER'
        self.name = 'PLAYER'
        self.adjacent = None
        self.x = None
        self.y = None

    def set_position(self, x, y, level=None, building=None):
        self.x = x
        self.y = y
        if level:
            self.level = level
        if building:
            self.building = building

    def set_position_to_node(self, node):
        self.set_position(
            x=node.x,
            y=node.y,
            level=node.level,
            building=node.building
        )

    def set_heading(self, heading):
        heading = heading % 360
        self.heading = heading


class Map(object):
    def __init__(self):
        self.north_map = {}
        self.nodes = {}
        self.graph = Graph()
        self.player = PlayerNode()

        self.path = []          # Path to take to get to destination
        self.next_node = None   # Next node to hit
        self.steps_to_next_node = 0

    def init(self, buildings=BUILDINGS, download=True, cache=False):
        if download:
            self.download_floorplans(buildings, use_cache=not download)
        else:
            try:
                with open(CACHE_FILE, 'r') as f:
                    logger.info('Reading from cache file')
                    data = f.read()
                    self.nodes = json.loads(data)
            except Exception as e:
                logger.error('{0}: {1}'.format(type(e).__name__, e))
                logger.warning('Error loading cache. Downloading instead')
                self.download_floorplans(buildings)

        # if cache:
        #     with open(CACHE_FILE, 'w') as f:
        #         logger.info('Writing to cache file')
        #         f.write(json.dumps(self.nodes))
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

    def _get_map_key(self, building, level):
        return '{0}_{1}'.format(building, level)

    def set_steps_to_next_node(self):
        distance = math.hypot(
            abs(self.next_node.x - self.player.x),
            abs(self.next_node.y - self.player.y),
        )
        self.steps_to_next_node = math.ceil(float(distance) / STEP_LENGTH)

    def is_valid_node(self, node_id):
        return node_id in self.nodes

    def download_floorplans(self, buildings, cache=False, use_cache=False):
        for building, levels in buildings.items():
            for level in levels:
                data = {
                    'Building': building,
                    'Level': level,
                }
                if not use_cache:
                    resp = requests.get(FLOORPLAN_URL, params=data)
                    if resp.status_code != 200:
                        return
                    result = resp.json()
                else:
                    path = CACHE_FILE.format(building, level)
                    with open(path) as f:
                        data = f.read()
                        result = json.loads(data)
                        logger.info('Loaded cache {0}'.format(path))
                key = self._get_map_key(building, level)
                self.north_map[key] = (
                    int(result.get('info', {}).get('northAt'))
                )

                for point in result.get('map', {}):
                    node = Node(
                        point.get('nodeId'),
                        int(point.get('x')),
                        int(point.get('y')),
                        point.get('nodeName'),
                        [i.strip() for i in point.get('linkTo').split(',')],
                        level,
                        building
                    )
                    self.nodes[node.id] = node

    def is_player_near_next_node(self):
        x = abs(self.player.x - self.next_node.x)
        y = abs(self.player.y - self.next_node.y)
        distance = math.hypot(x, y)
        if distance <= NODE_PROXIMITY_THRESHOLD:
            return True
        return False

    def is_player_facing_next_node(self):
        map_key = self._get_map_key(self.player.building, self.player.level)
        north = self.north_map.get(map_key)
        return is_pointing_to_node(
            from_x=self.player.x,
            from_y=self.player.y,
            to_x=self.next_node.x,
            to_y=self.next_node.y,
            heading=self.player.heading,
            north=north
        )

    def init_graph(self):
        for node_id in self.nodes:
            node = self.nodes.get(node_id)
            for adjacent_node_id in node.adjacent:
                self.graph.add_edge(node.id, adjacent_node_id)

            match = LINK_RE.match(node.name)
            if match:
                node_id = '{0}_{1}_{2}'.format(
                    match.group('building'),
                    match.group('level'),
                    match.group('node')
                )
                next_node = self.nodes.get(node_id)
                if next_node:
                    self.graph.add_edge(node.id, next_node.id)
                else:
                    logger.info(
                        'Cannot find node {0} in node list. Might be normal.'
                        .format(node_id)
                    )

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

        self.init_path(start, goal, came_from)
        return came_from, cost_so_far

    def init_path(self, start, goal, came_from):
        current = goal
        current_node = self.nodes.get(current)
        self.path = [current_node]
        while current != start:
            current = came_from[current]
            current_node = self.nodes.get(current)
            self.path.append(current_node)
        self.path.reverse()

    def calculate_player_turn_direction(self):
        map_key = self._get_map_key(self.player.building, self.player.level)
        turn = calculate_turn_direction(
            self.player.x,
            self.player.y,
            self.next_node.x,
            self.next_node.y,
            self.player.heading,
            self.north_map.get(map_key)
        )
        return turn
