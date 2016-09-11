import logging
import os
import ConfigParser

BASE_DIR = os.path.realpath(os.path.dirname(__file__))

config_file = os.path.join(BASE_DIR, 'config.ini')
config_parser = ConfigParser.ConfigParser()
config_parser.read(config_file)


def conf_get(section, key, default=None):
    try:
        return config_parser.get(section, key)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        return default

LOG_LEVEL = conf_get('general', 'log_level', default=logging.INFO)
