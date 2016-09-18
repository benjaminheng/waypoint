import time
from waypoint.utils.logger import get_logger
from waypoint.navigation.map import Map
from waypoint.firmware.comms import Comms
from waypoint.firmware.packet import DeviceID

logger = get_logger(__name__)

if __name__ == '__main__':
    logger.info('Starting Waypoint')
    nav_map = Map()
    comms = Comms('/dev/ttyAMA0')
    comms.run()

    while True:
        # Read device data like this
        print(comms.device_queue.get(DeviceID.ULTRASOUND_FRONT))
        time.sleep(1)
