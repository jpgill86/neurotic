# -*- coding: utf-8 -*-
"""
Tests for the GUI
"""

import pkg_resources
import tempfile
import shutil
import gc
import unittest

from ephyviewer import QT, mkQApp, MainViewer
import neurotic

import logging
logger = logging.getLogger(__name__)


class GUITestCase(unittest.TestCase):

    def setUp(self):
        self.file = pkg_resources.resource_filename(
            'neurotic', 'example/metadata.yml')

        # make a copy of the metadata file in a temp directory
        self.temp_dir = tempfile.TemporaryDirectory(prefix='neurotic-')
        self.temp_file = shutil.copy(self.file, self.temp_dir.name)

    def tearDown(self):
        # clean up references to proxy objects which keep files locked
        gc.collect()

        # remove the temp directory
        self.temp_dir.cleanup()

    def test_mkQApp(self):
        """Test that mkQApp returns a QApplication"""
        app = mkQApp()
        self.assertIsInstance(app, QT.QApplication)

    def test_example_create_ephyviewer_window(self):
        """Test creating an ephyviewer window for example dataset"""
        dataset = 'example dataset'
        metadata = neurotic.MetadataSelector(file=self.temp_file,
                                             initial_selection=dataset)
        metadata.download_all_data_files()

        lazy = False  # TODO: get lazy=True case to work
                      # (tearDown fails due to file lock)
        blk = neurotic.load_dataset(metadata=metadata, lazy=lazy)
        ephyviewer_config = neurotic.EphyviewerConfigurator(metadata, blk,
                                                            lazy=lazy)
        ephyviewer_config.show_all()

        app = mkQApp()
        win = ephyviewer_config.create_ephyviewer_window()
        self.assertIsInstance(win, MainViewer)

        # close thread properly
        win.close()

if __name__ == '__main__':
    unittest.main()
