# -*- coding: utf-8 -*-
"""
NEUROscience Tool for Interactive Characterization

Curate, visualize, annotate, and share your behavioral ephys data using Python
"""

import os
import sys
import shutil
import copy
import pkg_resources
import collections.abc
import logging
import logging.handlers
import toml

from .version import version as __version__
from .version import git_revision as __git_revision__


# set the user's directory for global settings file, logs, and more
neurotic_dir = os.path.join(os.path.expanduser('~'), '.neurotic')
if not os.path.exists(neurotic_dir):
    os.mkdir(neurotic_dir)

global_config = {
    'defaults': {
        # defaults used by the command line interface
        'file': None,
        'dataset': None,
        'debug': False,
        'lazy': True,
        'thick_traces': False,
        'show_datetime': False,
        'ui_scale': 'medium',
        'theme': 'light',
    },
}

# keep a copy of the original config before it is modified
_global_config_factory_defaults = copy.deepcopy(global_config)

# the global config file is a text file in TOML format owned by the user that
# allows alternate defaults to be specified to replace those in global_config
global_config_file = os.path.join(neurotic_dir, 'neurotic-config.txt')

if not os.path.exists(global_config_file):
    # copy a template global config file containing commented-out defaults
    shutil.copy(
        pkg_resources.resource_filename(
            'neurotic', 'global_config_template.txt'),
        global_config_file)

def update_dict(d, d_new):
    """
    Recursively update the contents of a dictionary. Unlike dict.update(), this
    function preserves items in inner dictionaries that are absent from d_new.

    For example, if given

    >>> d = {'x': 0, 'inner': {'a': 1, 'b': 2}}
    >>> d_new = {'inner': {'c': 3}}

    then using d.update(d_new) will entirely replace d['inner'] with
    d_new['inner']:

    >>> d.update(d_new)
    >>> d == {'x': 0, 'inner': {'c': 3}}

    In contrast, update_dict(d, d_new) will preserve items found in d['inner']
    but not in d_new['inner']:

    >>> update_dict(d, d_new)
    >>> d == {'x': 0, 'inner': {'a': 1, 'b': 2, 'c': 3}}
    """
    for k_new, v_new in d_new.items():
        if isinstance(v_new, collections.abc.Mapping):
            d[k_new] = update_dict(d.get(k_new, {}), v_new)
        else:
            d[k_new] = v_new
    return d

def update_global_config_from_file(file=global_config_file):
    """
    Update the global_config dictionary with data from the global config file,
    using recursion to traverse nested dictionaries.
    """
    with open(file, 'r') as f:
        update_dict(global_config, toml.loads(f.read()))

update_global_config_from_file()


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
