# -*- coding: utf-8 -*-
"""
Curate, visualize, annotate, and share your behavioral ephys data using Python
"""

from .version import version as __version__
from .version import git_revision as __git_revision__


import os
import sys
import logging
import logging.handlers

class FileLoggingFormatter(logging.Formatter):
    """
    A custom formatter for file logging
    """
    default_msec_format = '%s.%03d'  # use period instead of comma in decimal seconds
    def __init__(self):
        super().__init__(fmt='[%(asctime)s] [%(levelname)-8s] %(message)s')

class StreamLoggingFormatter(logging.Formatter):
    """
    A custom formatter for stream logging
    """
    def format(self, record):
        if record.levelno == logging.INFO:
            self._style._fmt = '[neurotic] %(message)s'  # do not print "INFO"
        else:
            self._style._fmt = '[neurotic] %(levelname)s: %(message)s'
        return super().format(record)


# set the file path for logging
log_dir = os.path.join(os.path.expanduser('~'), '.neurotic')
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_file = os.path.join(log_dir, 'neurotic-log.txt')

# set the default level for logging to INFO
logger = logging.getLogger(__name__)
if logger.level == logging.NOTSET:
    logger.setLevel(logging.INFO)

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
