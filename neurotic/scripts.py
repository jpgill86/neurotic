# -*- coding: utf-8 -*-
"""

"""

def launch_standalone():
    """

    """

    from ephyviewer import mkQApp
    from .gui.standalone import DataExplorer

    app = mkQApp()
    win = DataExplorer()
    win.show()
    print('Ready')
    app.exec_()
