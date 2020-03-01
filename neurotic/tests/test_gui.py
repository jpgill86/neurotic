# -*- coding: utf-8 -*-
"""
Tests for the GUI
"""

import unittest

from ephyviewer import mkQApp
from ephyviewer import QT

import logging
logger = logging.getLogger(__name__)


class GUITestCase(unittest.TestCase):

    def test_mkQApp(self):
        """Test that mkQApp returns a QApplication"""
        app = mkQApp()
        self.assertIsInstance(app, QT.QApplication)

if __name__ == '__main__':
    unittest.main()
