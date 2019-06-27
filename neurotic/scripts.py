# -*- coding: utf-8 -*-
"""

"""

import sys
import argparse

from ephyviewer import mkQApp

from . import __version__
from .gui.standalone import DataExplorer

def launch_standalone():
    """

    """

    description = """
    neurotic lets you curate, visualize, and annotate your behavioral ephys
    data.
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

    args = parser.parse_args(sys.argv[1:])

    app = mkQApp()
    win = DataExplorer(file=args.file, initial_selection=args.dataset)
    win.show()
    print('Ready')
    app.exec_()
