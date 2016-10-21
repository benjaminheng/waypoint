import logging

LOG_LEVEL = logging.INFO

FLOORPLAN_URL = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php'

# Map of building and levels to load
BUILDINGS = {
    '1': (1, 2),
    '2': (2, 3),
}

STEP_LENGTH = 66

# How close to the node before we consider ourselves to be at the node
NODE_PROXIMITY_THRESHOLD = 50

UF_FRONT_THRESHOLD = 100
UF_LEFT_THRESHOLD = 70
UF_RIGHT_THRESHOLD = 70


try:
    from local_settings import *  # NOQA
except ImportError:
    pass
