import sys
import os
app_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
print app_root
sys.path.append(app_root)

from logger import logger

logger.error('test')
