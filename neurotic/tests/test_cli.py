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
import fileinput
import re
import yaml
import unittest

from ephyviewer import mkQApp

import neurotic

import logging
logger = logging.getLogger(__name__)


class CLITestCase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix='neurotic-')

        # save the current global config settings so they can be restored
        # during tear-down
        self.original_config = copy.deepcopy(neurotic.global_config)

        # reset global config settings to their factory defaults (use deepcopy
        # so that _global_config_factory_defaults is not changed during tests)
        neurotic.global_config.clear()
        neurotic.global_config.update(copy.deepcopy(
            neurotic._global_config_factory_defaults))

        # get parameters for the example
        self.example_file = pkg_resources.resource_filename(
            'neurotic', 'example/metadata.yml')
        self.example_dataset = 'Aplysia feeding'

        # make a copy of the example metadata file in the temp directory and
        # then add an additional dataset to it
        self.temp_file = shutil.copy(self.example_file, self.temp_dir.name)
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
        neurotic.global_config.clear()
        neurotic.global_config.update(self.original_config)

    def test_global_config_template(self):
        """Test that the global config template matches the factory defaults"""

        # load the template global config file by first copying it to the temp
        # directory, uncommenting every parameter, and then updating
        # global_config using the modified file
        self.template_global_config_file = pkg_resources.resource_filename(
            'neurotic', 'global_config_template.txt')
        self.temp_global_config_file = shutil.copy(
            self.template_global_config_file, self.temp_dir.name)
        with fileinput.input(self.temp_global_config_file, inplace=True) as f:
            for line in f:
                if re.match('#.*=.*', line):
                    line = line[1:]
                print(line, end='')  # stdout is redirected into the file
        neurotic.update_global_config_from_file(self.temp_global_config_file)

        # substitute special values
        if neurotic.global_config['defaults']['file'] == 'example':
            neurotic.global_config['defaults']['file'] = None
        if neurotic.global_config['defaults']['dataset'] == 'none':
            neurotic.global_config['defaults']['dataset'] = None

        self.assertEqual(neurotic.global_config,
                         neurotic._global_config_factory_defaults,
                         'global_config loaded from template global config '
                         'file differs from factory defaults')

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
        """Test CLI default values match factory defaults"""
        argv = ['neurotic']
        args = neurotic.parse_args(argv)
        app = mkQApp()
        win = neurotic.win_from_args(args)

        # should match factory defaults because setUp() explicitly reset the
        # defaults to the factory defaults
        factory_defaults = neurotic._global_config_factory_defaults['defaults']
        self.assertEqual(win.do_toggle_debug_logging.isChecked(),
                         factory_defaults['debug'],
                         'debug setting has unexpected default')
        self.assertEqual(win.lazy, factory_defaults['lazy'],
                         'lazy setting has unexpected default')
        self.assertEqual(win.support_increased_line_width,
                         factory_defaults['thick_traces'],
                         'thick traces setting has unexpected default')
        self.assertEqual(win.show_datetime, factory_defaults['show_datetime'],
                         'show_datetime has unexpected default')
        self.assertEqual(win.ui_scale, factory_defaults['ui_scale'],
                         'ui_scale has unexpected default')
        self.assertEqual(win.theme, factory_defaults['theme'],
                         'theme has unexpected default')
        self.assertEqual(win.metadata_selector.file, self.example_file,
                         'file has unexpected default')
        self.assertEqual(win.metadata_selector._selection,
                         self.example_dataset,
                         'dataset has unexpected default')

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

    def test_use_factory_defaults(self):
        """Test that --use-factory-defaults resets all defaults"""
        for k in neurotic.global_config['defaults']:
            neurotic.global_config['defaults'][k] = 'bad value'
        argv = ['neurotic', '--use-factory-defaults']
        args = neurotic.parse_args(argv)
        for k, v in neurotic._global_config_factory_defaults['defaults'].items():
            self.assertEqual(getattr(args, k), v,
                             f'args.{k} was not reset to factory default')

    def test_file(self):
        """Test that metadata file can be set"""
        argv = ['neurotic', self.temp_file]
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
