# -*- coding: utf-8 -*-
"""

"""

import sys
import argparse

from ephyviewer import mkQApp

from . import __version__
from .gui.standalone import DataExplorer

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
    parser.add_argument('--theme', choices=['light', 'dark', 'original'],
                        default='light', help='a color theme for the GUI ' \
                                              '(default: light)')

    args = parser.parse_args(argv[1:])

    return args

def win_from_args(args):
    """

    """

    win = DataExplorer(file=args.file, initial_selection=args.dataset,
                       lazy=args.lazy, theme=args.theme,
                       support_increased_line_width=args.thick)
    return win

def main():
    """

    """

    args = parse_args(sys.argv)
    app = mkQApp()
    win = win_from_args(args)
    win.show()
    print('Ready')
    app.exec_()
