# -*- coding: utf-8 -*-
"""
Tests for the command line interface
"""

import os
import sys
import shutil
from subprocess import check_output
import tempfile
import pkg_resources
import copy
import yaml
import unittest

from ephyviewer import mkQApp

import neurotic

import logging
logger = logging.getLogger(__name__)


class CLITestCase(unittest.TestCase):

    def setUp(self):
        self.default_file = pkg_resources.resource_filename(
            'neurotic', 'example/metadata.yml')
        self.default_dataset = 'Aplysia feeding'

        # make a copy of the default file in a temp directory
        self.temp_dir = tempfile.TemporaryDirectory(prefix='neurotic-')
        self.temp_file = shutil.copy(self.default_file, self.temp_dir.name)

        # add a second dataset
        with open(self.temp_file) as f:
            metadata = yaml.safe_load(f)
        metadata['zzz_alphabetically_last'] = copy.deepcopy(
            metadata['Aplysia feeding'])
        with open(self.temp_file, 'w') as f:
            f.write(yaml.dump(metadata))

    def tearDown(self):
        # remove the temp directory
        self.temp_dir.cleanup()

    def test_cli_installed(self):
        """Test that the command line interface is installed"""
        self.assertIsNotNone(shutil.which('neurotic'), 'path to cli not found')

    def test_help(self):
        """Test that --help returns usage info"""
        argv = ['neurotic', '--help']
        out = check_output(argv)
        self.assertTrue(out.decode('utf-8').startswith('usage: neurotic'),
                        'help\'s stdout has unexpected content')

    def test_version(self):
        """Test that --version returns version info"""
        argv = ['neurotic', '--version']
        out = check_output(argv)
        self.assertTrue(out.decode('utf-8').startswith('neurotic'),
                        'version\'s stdout has unexpected content')

    def test_cli_defaults(self):
        """Test CLI default values"""
        argv = ['neurotic']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertFalse(win.do_toggle_debug_logging.isChecked(),
                         'debug logging enabled without --debug')
        self.assertTrue(win.lazy, 'lazy loading disabled without --no-lazy')
        self.assertFalse(win.support_increased_line_width,
                         'thick traces enabled without --thick-traces')
        self.assertFalse(win.show_datetime,
                         'datetime enabled without --show-datetime')
        self.assertEqual(win.ui_scale, 'medium',
                         'ui_scale changed without --ui-scale')
        self.assertEqual(win.theme, 'light', 'theme changed without --theme')
        self.assertEqual(win.metadata_selector.file, self.default_file,
                         'file was not set to default')
        self.assertEqual(win.metadata_selector._selection,
                         self.default_dataset,
                         'dataset was not set to default dataset')

    def test_debug(self):
        """Test that --debug enables logging of debug messages"""
        argv = ['neurotic', '--debug']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertTrue(win.do_toggle_debug_logging.isChecked(),
                        'debug logging disabled with --debug')

    def test_no_lazy(self):
        """Test that --no-lazy disables lazy loading"""
        argv = ['neurotic', '--no-lazy']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertFalse(win.lazy, 'lazy loading enabled with --no-lazy')

    def test_thick_traces(self):
        """Test that --thick-traces enables support for thick traces"""
        argv = ['neurotic', '--thick-traces']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertTrue(win.support_increased_line_width,
                        'thick traces disabled with --thick-traces')

    def test_show_datetime(self):
        """Test that --show-datetime enables display of real-world datetime"""
        argv = ['neurotic', '--show-datetime']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertTrue(win.show_datetime,
                        'datetime not displayed with --show-datetime')

    def test_ui_scale(self):
        """Test that --ui-scale changes the ui_scale"""
        app = mkQApp()

        for size in neurotic.available_ui_scales:
            argv = ['neurotic', '--ui-scale', size]
            args = neurotic.parse_args(argv)
            win = neurotic.win_from_args(args)
            self.assertEqual(win.ui_scale, size, 'unexpected scale')

    def test_theme(self):
        """Test that --theme changes the theme"""
        app = mkQApp()

        for theme in neurotic.available_themes:
            argv = ['neurotic', '--theme', theme]
            args = neurotic.parse_args(argv)
            win = neurotic.win_from_args(args)
            self.assertEqual(win.theme, theme, 'unexpected theme')

    def test_file(self):
        """Test that metadata file can be set"""
        argv = ['neurotic', self.temp_file]
        args = neurotic.parse_args(argv)
        win = neurotic.win_from_args(args)
        self.assertEqual(win.metadata_selector.file, self.temp_file,
                         'file was not changed correctly')

    def test_dataset(self):
        """Test that dataset can be set"""
        argv = ['neurotic', self.temp_file, 'zzz_alphabetically_last']
        args = neurotic.parse_args(argv)
        win = neurotic.win_from_args(args)
        self.assertEqual(win.metadata_selector._selection,
                         'zzz_alphabetically_last',
                         'dataset was not changed correctly')

if __name__ == '__main__':
    unittest.main()
