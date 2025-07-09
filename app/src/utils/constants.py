"""All the project constants"""

import logging
from pathlib import Path

# [Dirs]
BASE_DIR = Path('./').absolute().resolve()
DATA_DIR = BASE_DIR.joinpath('data').absolute().resolve()
TEMP_DIR = BASE_DIR.joinpath('temp').absolute().resolve()


# [Logs]
LOG_DIR = TEMP_DIR.joinpath('logs/').absolute().resolve()
LOG_FMT = '%(asctime)s [%(levelname)s]: %(name)s: %(message)s'
LOG_LEVEL = logging.INFO

# Update logs time
# @link: https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
UPDATE_TIME = 'midnight'
UPDATE_INTERVAL = 1
KEEP_OLD_LOGS = 5

# [Google API]
SERVICE_ACCOUNT_CREDENTIALS = DATA_DIR.joinpath('credentials.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# [Datetime]
DATETIME_FMT = '%Y-%m-%d-%H-%M-%S'

# [OTHER]
