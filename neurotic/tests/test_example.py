# -*- coding: utf-8 -*-
"""
Tests for example datasets
"""

import pkg_resources
import tempfile
import shutil
import gc
import unittest

import neurotic

import logging
logger = logging.getLogger(__name__)


class ExampleDatasetsUnitTest(unittest.TestCase):

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

    def test_example_lazy_loading(self):
        """Test loading the example dataset with lazy=True"""
        dataset = 'example dataset'
        metadata = neurotic.MetadataSelector(file=self.temp_file,
                                             initial_selection=dataset)
        metadata.download_all_data_files()

        blk = neurotic.load_dataset(metadata=metadata, lazy=True)
        assert(blk)

    def test_example_non_lazy_loading(self):
        """Test loading the example dataset with lazy=False"""
        dataset = 'example dataset'
        metadata = neurotic.MetadataSelector(file=self.temp_file,
                                             initial_selection=dataset)
        metadata.download_all_data_files()

        blk = neurotic.load_dataset(metadata=metadata, lazy=False)
        assert(blk)

if __name__ == '__main__':
    unittest.main()
