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
    parser.add_argument('-V', '--version', action='version',
                        version='neurotic {}'.format(__version__))

    args = parser.parse_args(sys.argv[1:])

    app = mkQApp()
    win = DataExplorer()
    win.show()
    print('Ready')
    app.exec_()
