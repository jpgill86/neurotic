# -*- coding: utf-8 -*-
"""
The :mod:`neurotic.scripts` module handles starting the app from the command
line. It also provides a convenience function for quickly launching the app
using minimal metadata or an existing Neo :class:`Block <neo.core.Block>`, and
another for starting a Jupyter server with an example notebook.

.. autofunction:: quick_launch

.. autofunction:: launch_example_notebook
"""

import os
import sys
import argparse
import subprocess
import pkg_resources

from ephyviewer import QT, mkQApp

from . import __version__, global_config, global_config_file, default_log_level
from .datasets.data import load_dataset
from .gui.config import EphyviewerConfigurator, available_themes, available_ui_scales
from .gui.standalone import MainWindow

import logging
logger = logging.getLogger(__name__)


def parse_args(argv):
    """

    """

    description = """
    neurotic lets you curate, visualize, annotate, and share your behavioral
    ephys data.
    """

    epilog = f"""
    Defaults for arguments and options can be changed in
    {os.path.relpath(global_config_file, os.path.expanduser('~'))}, located in
    your home directory.
    """

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    defaults = global_config['defaults']
    parser.set_defaults(**defaults)

    parser.add_argument('file', nargs='?',
                        help='the path to a metadata YAML file'
                             f' (default: {"an example file" if defaults["file"] is None else defaults["file"] + "; to force the example, use: example"})')

    parser.add_argument('dataset', nargs='?',
                        help='the name of a dataset in the metadata file to '
                             'select initially'
                             f' (default: {"the first entry in the metadata file" if defaults["dataset"] is None else defaults["dataset"] + "; to force the first, use: - none"})')

    parser.add_argument('-V', '--version',
                        action='version',
                        version='neurotic {}'.format(__version__))

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--debug', dest='debug',
                       action='store_true',
                       help='enable detailed log messages for debugging'
                            f'{" (default)" if defaults["debug"] else ""}')
    group.add_argument('--no-debug', dest='debug',
                       action='store_false',
                       help='disable detailed log messages for debugging'
                            f'{" (default)" if not defaults["debug"] else ""}')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--lazy', dest='lazy',
                       action='store_true',
                       help='enable fast loading'
                            f'{" (default)" if defaults["lazy"] else ""}')
    group.add_argument('--no-lazy', dest='lazy',
                       action='store_false',
                       help='disable fast loading'
                            f'{" (default)" if not defaults["lazy"] else ""}')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--thick-traces', dest='thick_traces',
                       action='store_true',
                       help='enable support for traces with thick lines, '
                            'which has a performance cost'
                            f'{" (default)" if defaults["thick_traces"] else ""}')
    group.add_argument('--no-thick-traces', dest='thick_traces',
                       action='store_false',
                       help='disable support for traces with thick lines'
                            f'{" (default)" if not defaults["thick_traces"] else ""}')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--show-datetime', dest='show_datetime',
                       action='store_true',
                       help='display the real-world date and time, which '
                            'may be inaccurate depending on file type and '
                            'acquisition software'
                            f'{" (default)" if defaults["show_datetime"] else ""}')
    group.add_argument('--no-show-datetime', dest='show_datetime',
                       action='store_false',
                       help='do not display the real-world date and time'
                            f'{" (default)" if not defaults["show_datetime"] else ""}')

    parser.add_argument('--ui-scale', dest='ui_scale',
                        choices=available_ui_scales,
                        help='the scale of user interface elements, such as '
                             'text'
                             f' (default: {defaults["ui_scale"]})')

    parser.add_argument('--theme', dest='theme',
                        choices=available_themes,
                        help='a color theme for the GUI'
                             f' (default: {defaults["theme"]})')

    group = parser.add_argument_group('alternative modes')
    group.add_argument('--launch-example-notebook',
                       action='store_true',
                       help='launch Jupyter with an example notebook '
                            'instead of starting the standalone app (other '
                            'args will be ignored)')

    args = parser.parse_args(argv[1:])

    # these special values for the positional arguments can be used to override
    # the defaults set in the global config file with the defaults normally set
    # in the absence of global config file settings
    if args.file == '-':
        args.file = defaults['file']
    elif args.file == 'example':
        args.file = None
    if args.dataset == '-':
        args.dataset = defaults['dataset']
    elif args.dataset == 'none':
        args.dataset = None

    if args.debug:
        logger.parent.setLevel(logging.DEBUG)

        # lower the threshold for PyAV messages printed to the console from
        # critical to warning
        logging.getLogger('libav').setLevel(logging.WARNING)

        if not args.launch_example_notebook:
            # show only if Jupyter won't be launched, since the setting will
            # not carry over into the kernel started by Jupyter
            logger.debug('Debug messages enabled')

    else:
        # this should only be necessary if parse_args is called with --no-debug
        # after having previously enabled debug messages in the current session
        # (such as during unit testing)

        logger.parent.setLevel(default_log_level)

        # raise the threshold for PyAV messages printed to the console from
        # warning to critical
        logging.getLogger('libav').setLevel(logging.CRITICAL)

    return args

def win_from_args(args):
    """

    """

    win = MainWindow(file=args.file, initial_selection=args.dataset,
                     lazy=args.lazy, theme=args.theme, ui_scale=args.ui_scale,
                     support_increased_line_width=args.thick_traces,
                     show_datetime=args.show_datetime)
    return win

def launch_example_notebook():
    """
    Start a Jupyter server and open the example notebook.
    """

    path = pkg_resources.resource_filename('neurotic',
                                           'example/example-notebook.ipynb')
    out = None

    # check whether Jupyter is installed
    try:
        out = subprocess.Popen(['jupyter', 'notebook', '--version'],
                               stdout=subprocess.PIPE).communicate()[0]
    except FileNotFoundError as e:
        logger.error('Unable to verify Jupyter is installed using "jupyter '
                     'notebook --version". Is it installed?')

    if out:
        # run Jupyter on the example notebook
        try:
            out = subprocess.Popen(['jupyter', 'notebook', path],
                                   stdout=subprocess.PIPE).communicate()[0]
        except FileNotFoundError as e:
            logger.error(f'Unable to locate the example notebook at {path}')

def main():
    """

    """

    args = parse_args(sys.argv)
    if args.launch_example_notebook:
        launch_example_notebook()
    else:
        logger.info('Loading user interface')
        app = mkQApp()
        splash = QT.QSplashScreen(QT.QPixmap(':/neurotic-logo-300.png'))
        splash.show()
        win = win_from_args(args)
        win.show()
        splash.finish(win)
        logger.info('Ready')
        app.exec_()

def quick_launch(metadata={}, blk=None, lazy=True):
    """
    Load data, configure the GUI, and launch the app with one convenient
    function.

    This function allows *neurotic* to be used easily in interactive sessions
    and scripts. For example, dictionaries can be passed as metadata:

    >>> metadata = {'data_file': 'data.axgx'}
    >>> neurotic.quick_launch(metadata=metadata)

    An existing Neo :class:`Block <neo.core.Block>` can be passed directly:

    >>> neurotic.quick_launch(blk=my_neo_block)

    This function is equivalent to the following:

    >>> blk = load_dataset(metadata, blk, lazy=lazy)
    >>> ephyviewer_config = EphyviewerConfigurator(metadata, blk, lazy=lazy)
    >>> ephyviewer_config.show_all()
    >>> ephyviewer_config.launch_ephyviewer()
    """

    # make sure this matches the docstring after making changes
    blk = load_dataset(metadata, blk, lazy=lazy)
    ephyviewer_config = EphyviewerConfigurator(metadata, blk, lazy=lazy)
    ephyviewer_config.show_all()
    ephyviewer_config.launch_ephyviewer()
