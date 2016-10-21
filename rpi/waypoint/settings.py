import logging

LOG_LEVEL = logging.DEBUG

FLOORPLAN_URL = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php'

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
