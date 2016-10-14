import logging

LOG_LEVEL = logging.INFO

FLOORPLAN_URL = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php'

# Map of building and levels to load
BUILDINGS = {
    'COM1': (1, 2),
    'COM2': (2, 3),
}

try:
    from local_settings import *  # NOQA
except ImportError:
    pass
