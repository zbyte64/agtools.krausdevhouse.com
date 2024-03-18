import logging
import os

LOG_LEVEL = os.environ.get("DEBUG_TRACE") and logging.DEBUG or logging.INFO

logging.basicConfig(format="%(asctime)s %(message)s", level=LOG_LEVEL)

getLogger = logging.getLogger
