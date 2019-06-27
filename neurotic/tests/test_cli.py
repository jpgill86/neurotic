# -*- coding: utf-8 -*-
"""
Tests for the command line interface
"""

import os
from shutil import which
from subprocess import check_output
import unittest

class CLITestCase(unittest.TestCase):

    def test_cli_installed(self):
        """Verify that the command line interface is installed"""
        self.assertIsNotNone(which('neurotic'), 'path to cli not found')

    def test_help(self):
        """Verify that --help returns usage info"""
        out = check_output(['neurotic', '--help'])
        self.assertTrue(out.decode('utf-8').startswith('usage: neurotic'),
                        'help\'s stdout has unexpected content')

if __name__ == '__main__':
    unittest.main()
