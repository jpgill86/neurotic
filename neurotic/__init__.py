# -*- coding: utf-8 -*-
"""
NEUROscience Tool for Interactive Characterization

Curate, visualize, annotate, and share your behavioral ephys data using Python
"""

import os
import sys
import logging
import logging.handlers

from .version import version as __version__
from .version import git_revision as __git_revision__


# set the user's directory for logs
neurotic_dir = os.path.join(os.path.expanduser('~'), '.neurotic')
if not os.path.exists(neurotic_dir):
    os.mkdir(neurotic_dir)


class FileLoggingFormatter(logging.Formatter):
    """
    A custom formatter for file logging
    """
    default_msec_format = '%s.%03d'  # use period radix point instead of comma in decimal seconds
    def format(self, record):
        if logging.getLogger(__name__).level <= logging.DEBUG:
            # include more detail if the logger level (not the record level) is
            # debug or lower
            self._style._fmt = '[%(asctime)s] [%(levelname)-8s] [%(threadName)-10s] [%(name)s:%(lineno)d (%(funcName)s)] %(message)s'
        else:
            self._style._fmt = '[%(asctime)s] [%(levelname)-8s] %(message)s'
        return super().format(record)

class StreamLoggingFormatter(logging.Formatter):
    """
    A custom formatter for stream logging
    """
    def format(self, record):
        if record.levelno == logging.INFO:
            # exclude the level name ("INFO") from common log records
            self._style._fmt = '[neurotic] %(message)s'
        else:
            self._style._fmt = '[neurotic] %(levelname)s: %(message)s'
        return super().format(record)


# set the file path for logging
log_file = os.path.join(neurotic_dir, 'neurotic-log.txt')

# set the default level for logging to INFO unless it was set to a custom level
# before importing the package
logger = logging.getLogger(__name__)
if logger.level == logging.NOTSET:
    default_log_level = logging.INFO
    logger.setLevel(default_log_level)
else:
    default_log_level = logger.level

# write log records to a file, rotating files if it exceeds 10 MB
logger_filehandler = logging.handlers.RotatingFileHandler(filename=log_file, maxBytes=10000000, backupCount=2)
logger_filehandler.setFormatter(FileLoggingFormatter())
logger.addHandler(logger_filehandler)
logger.info('===========================')        # file logger only
logger.info(f'Importing neurotic {__version__}')  # file logger only

# stream log records to stderr
logger_streamhandler = logging.StreamHandler(stream=sys.stderr)
logger_streamhandler.setFormatter(StreamLoggingFormatter())
logger.addHandler(logger_streamhandler)


from .datasets import *
from .gui import *
from .scripts import *
