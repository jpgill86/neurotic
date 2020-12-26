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
        self.default_config = copy.deepcopy(neurotic.global_config)
        self.example_file = pkg_resources.resource_filename(
            'neurotic', 'example/metadata.yml')
        self.example_dataset = 'Aplysia feeding'

        # make a copy of the default file in a temp directory
        self.temp_dir = tempfile.TemporaryDirectory(prefix='neurotic-')
        self.temp_file = shutil.copy(self.example_file, self.temp_dir.name)

        # add another dataset to the example
        with open(self.temp_file) as f:
            metadata = yaml.safe_load(f)
        self.duplicate_dataset = 'zzz_alphabetically_last'
        metadata[self.duplicate_dataset] = copy.deepcopy(
            metadata[self.example_dataset])
        with open(self.temp_file, 'w') as f:
            f.write(yaml.dump(metadata))

    def tearDown(self):
        # remove the temp directory
        self.temp_dir.cleanup()

        # restore the original global config
        neurotic.global_config = copy.deepcopy(self.default_config)

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
        defaults = neurotic.global_config['defaults']
        self.assertEqual(win.do_toggle_debug_logging.isChecked(),
                         defaults['debug'],
                         'debug logging setting did not match default')
        self.assertEqual(win.lazy,
                         defaults['lazy'],
                         'lazy loading setting did not match default')
        self.assertEqual(win.support_increased_line_width,
                         defaults['thick_traces'],
                         'thick traces setting did not match default')
        self.assertEqual(win.show_datetime,
                         defaults['show_datetime'],
                         'datetime setting did not match default')
        self.assertEqual(win.ui_scale,
                         defaults['ui_scale'],
                         'ui scale did not match default')
        self.assertEqual(win.theme,
                         defaults['theme'],
                         'theme did not match default')
        self.assertEqual(win.metadata_selector.file,
                         self.example_file if defaults['file'] is None else defaults['file'],
                         'file was not set to default')
        self.assertEqual(win.metadata_selector._selection,
                         self.example_dataset if defaults['dataset'] is None else defaults['dataset'],
                         'dataset was not set to default dataset')

    def test_debug(self):
        """Test that --debug enables logging of debug messages"""
        argv = ['neurotic', '--debug']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertTrue(win.do_toggle_debug_logging.isChecked(),
                        'debug logging disabled with --debug')

    def test_no_debug(self):
        """Test that --no-debug disables logging of debug messages"""
        argv = ['neurotic', '--no-debug']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertFalse(win.do_toggle_debug_logging.isChecked(),
                         'debug logging enabled with --no-debug')

    def test_lazy(self):
        """Test that --lazy enables lazy loading"""
        argv = ['neurotic', '--lazy']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertTrue(win.lazy, 'lazy loading disbled with --lazy')

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

    def test_no_thick_traces(self):
        """Test that --no-thick-traces disables support for thick traces"""
        argv = ['neurotic', '--no-thick-traces']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertFalse(win.support_increased_line_width,
                         'thick traces enabled with --no-thick-traces')

    def test_show_datetime(self):
        """Test that --show-datetime enables display of real-world datetime"""
        argv = ['neurotic', '--show-datetime']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertTrue(win.show_datetime,
                        'datetime not displayed with --show-datetime')

    def test_no_show_datetime(self):
        """Test that --no-show-datetime hides the real-world datetime"""
        argv = ['neurotic', '--no-show-datetime']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)
        self.assertFalse(win.show_datetime,
                         'datetime displayed with --no-show-datetime')

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
        argv = ['neurotic', self.temp_file, 'none']
        args = neurotic.parse_args(argv)
        win = neurotic.win_from_args(args)
        self.assertEqual(win.metadata_selector.file, self.temp_file,
                         'file was not changed correctly')

    def test_dataset(self):
        """Test that dataset can be set"""
        argv = ['neurotic', self.temp_file, self.duplicate_dataset]
        args = neurotic.parse_args(argv)
        win = neurotic.win_from_args(args)
        self.assertEqual(win.metadata_selector._selection,
                         self.duplicate_dataset,
                         'dataset was not changed correctly')

    def test_example_file_and_first_dataset_overrides(self):
        """Test that 'example' and 'none' open first dataset in example file"""
        neurotic.global_config['defaults']['file'] = 'some other file'
        neurotic.global_config['defaults']['dataset'] = 'some other dataset'
        argv = ['neurotic', 'example', 'none']
        args = neurotic.parse_args(argv)
        win = neurotic.win_from_args(args)
        self.assertEqual(win.metadata_selector.file, self.example_file,
                         'file was not changed correctly')
        self.assertEqual(win.metadata_selector._selection,
                         self.example_dataset,
                         'dataset was not changed correctly')

if __name__ == '__main__':
    unittest.main()
