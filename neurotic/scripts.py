# -*- coding: utf-8 -*-
"""

"""

import sys
import argparse

from ephyviewer import mkQApp

from .gui.standalone import DataExplorer

def launch_standalone():
    """

    """

    description = """
    neurotic lets you curate, visualize, and annotate your behavioral ephys
    data.
    """
    parser = argparse.ArgumentParser(description=description)

    args = parser.parse_args(sys.argv[1:])

    app = mkQApp()
    win = DataExplorer()
    win.show()
    print('Ready')
    app.exec_()
