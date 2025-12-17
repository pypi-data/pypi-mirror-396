import os
from . import __version__
from .helpers import *


DOCKSIBLE_BANNER = """
        __ \\                |          _)  |      |       
        |   |   _ \\    __|  |  /   __|  |  __ \\   |   _ \\ 
        |   |  (   |  (       <  \\__ \\  |  |   |  |   __/ 
       ____/  \\___/  \\___| _|\\_\\ ____/ _| _.__/  _| \\___| 

    =======================================================

        --------------------------------------------
            Docker apps with Ansible  -  v{}
        --------------------------------------------
""".format(__version__)

USER_HOME_DIR = os.path.expanduser('~')
TEMPLATES_DIR = find_templates_dir()
DEFAULT_PRIVATE_DATA_DIR = os.path.join(USER_HOME_DIR, '.docksible')
DEFAULT_BACKUPS_DIR = os.path.join(USER_HOME_DIR, '.docksible-backups')

SUPPORTED_ACTIONS = [
    'setup-docker-compose',
    'nginx',
    'wordpress',
    'joomla',
    'redmine',
    'custom-app',
]

DEFAULT_DATABASE_USERNAME = 'db-username'
DEFAULT_DATABASE_NAME = 'db_name'
DEFAULT_DATABASE_TABLE_PREFIX = ''

DEFAULT_SITE_TITLE      = 'Sample Site'
DEFAULT_ADMIN_USERNAME  = 'admin'
DEFAULT_ADMIN_FULL_NAME = 'Site administrator'
DEFAULT_ADMIN_EMAIL     = 'admin@example.com'

DEFAULT_WORDPRESS_LOCALE = 'en_US'

DEFAULT_APP_VERSION = 'latest'
