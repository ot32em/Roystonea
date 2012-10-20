"""
This is the log config file of Roystonea.
The logger will print the log whose level is below error on console, 
and write the log whose level is above error(include error) to corresponsive log file.

Any script that needs to use log can import this config file by:
from Roystonea.logger import logger

There are 5 levels of log, and you can use them as:
    logger.debug('')
    logger.info('')
    logger.warning('')
    logger.error('')
    logger.critical('')

To get the detail of logging:
    http://docs.python.org/howto/logging.html#logging-basic-tutorial
"""

import logging
# import sys
import inspect
import os
import roystonea

LOGGING_PATH = os.path.join(roystonea.ROYSTONEA_ROOT, "log/")
print LOGGING_PATH

# log_owner = sys._getframe(1).f_globals.get('__name__')
log_owner = inspect.stack()[1][1][:-3]

logger = logging.getLogger(log_owner + '.py')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOGGING_PATH + log_owner + ".log")
console_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

