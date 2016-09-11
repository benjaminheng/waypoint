from waypoint.utils.logger import get_logger
from waypoint.navigation.map import Map

logger = get_logger(__name__)

if __name__ == '__main__':
    logger.info('Starting Waypoint')
    nav_map = Map()
