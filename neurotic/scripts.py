# -*- coding: utf-8 -*-
"""

"""

import sys
import argparse
import subprocess
import pkg_resources

from ephyviewer import mkQApp

from . import __version__
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
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('file', nargs='?', default=None,
                        help='the path to a metadata YAML file (default: an ' \
                             'example file)')
    parser.add_argument('dataset', nargs='?', default=None,
                        help='the name of a dataset in the metadata file to ' \
                             'select initially (default: the first entry in ' \
                             'the metadata file)')

    parser.add_argument('-V', '--version', action='version',
                        version='neurotic {}'.format(__version__))
    parser.add_argument('--no-lazy', action='store_false', dest='lazy',
                        help='do not use fast loading (default: use fast ' \
                             'loading)')
    parser.add_argument('--thick-traces', action='store_true', dest='thick',
                        help='enable support for traces with thick lines, ' \
                             'which has a performance cost (default: ' \
                             'disable thick line support)')
    parser.add_argument('--show-datetime', action='store_true', dest='datetime',
                        help='display the real-world date and time, which ' \
                             'may be inaccurate depending on file type and ' \
                             'acquisition software (default: do not display)')
    parser.add_argument('--theme', choices=['light', 'dark', 'original',
                                            'printer-friendly'],
                        default='light', help='a color theme for the GUI ' \
                                              '(default: light)')

    parser.add_argument('--launch-example-notebook', action='store_true',
                        help='launch Jupyter with an example notebook ' \
                             'instead of starting the standalone app (other ' \
                             'args will be ignored)')

    args = parser.parse_args(argv[1:])

    return args

def win_from_args(args):
    """

    """

    win = MainWindow(file=args.file, initial_selection=args.dataset,
                     lazy=args.lazy, theme=args.theme,
                     support_increased_line_width=args.thick,
                     show_datetime=args.datetime)
    return win

def launch_example_notebook():
    """

    """

    path = pkg_resources.resource_filename('neurotic',
                                           'example/example-notebook.ipynb')
    out = None

    # check whether Jupyter is installed
    try:
        out = subprocess.Popen(['jupyter', 'notebook', '--version'],
                               stdout=subprocess.PIPE).communicate()[0]
    except FileNotFoundError as e:
        logger.critical('Unable to verify Jupyter is installed using "jupyter '
                        'notebook --version". Is it installed?')

    if out:
        # run Jupyter on the example notebook
        try:
            out = subprocess.Popen(['jupyter', 'notebook', path],
                                   stdout=subprocess.PIPE).communicate()[0]
        except FileNotFoundError as e:
            logger.critical(f'Unable to locate the example notebook at {path}')

def main():
    """

    """

    args = parse_args(sys.argv)
    if args.launch_example_notebook:
        launch_example_notebook()
    else:
        logger.info('Loading user interface')
        app = mkQApp()
        win = win_from_args(args)
        win.show()
        logger.info('Ready')
        app.exec_()
