import logging

LOG_LEVEL = logging.DEBUG

FLOORPLAN_URL = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php'

# Cache file
DOWNLOAD_MAP = True  # If false, use cache
CACHE_DOWNLOADED_MAP = True
CACHE_FILE = '/home/pi/waypoint/{0}_{1}.json'
CACHE_FILES = [
    '/home/pi/waypoint/1_1.json',
    '/home/pi/waypoint/1_2.json',
    '/home/pi/waypoint/2_2.json',
    '/home/pi/waypoint/2_3.json',
]

# Map of building and levels to load
BUILDINGS = {
    '1': (1, 2),
    '2': (2, 3),
}

STEP_LENGTH = 66

# How close to the node before we consider ourselves to be at the node
NODE_PROXIMITY_THRESHOLD = 50

UF_FRONT_THRESHOLD = 150
UF_LEFT_THRESHOLD = 100
UF_RIGHT_THRESHOLD = 100


try:
    from local_settings import *  # NOQA
except ImportError:
    pass
