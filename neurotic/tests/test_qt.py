# -*- coding: utf-8 -*-
"""
Tests for Qt
"""

import unittest
import logging

from ephyviewer import mkQApp
from ephyviewer import QT

logger = logging.getLogger(__name__)

class QtTestCase(unittest.TestCase):

    def test_mkQApp(self):
        """ Test that mkQApp returns a QApplication """
        app = mkQApp()
        self.assertIsInstance(app, QT.QApplication)

if __name__ == '__main__':
    unittest.main()
