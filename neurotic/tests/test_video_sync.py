# -*- coding: utf-8 -*-
"""
Tests for video sync features
"""

import pkg_resources
import tempfile
import shutil
import gc
import unittest
import logging

import numpy as np
from numpy.testing import assert_array_almost_equal

import neurotic

logger = logging.getLogger(__name__)

class VideoSyncUnitTest(unittest.TestCase):

    def setUp(self):
        self.file = pkg_resources.resource_filename(
            'neurotic.tests', 'metadata-for-tests.yml')

        # make a copy of the metadata file in a temp directory
        self.temp_dir = tempfile.TemporaryDirectory(prefix='neurotic-')
        self.temp_file = shutil.copy(self.file, self.temp_dir.name)

    def tearDown(self):
        # clean up references to proxy objects which keep files locked
        gc.collect()

        # remove the temp directory
        self.temp_dir.cleanup()

    def test_video_jumps(self):
        """Test video jump estimation for AxoGraph file with pauses"""
        dataset = 'events-and-epochs'
        metadata = neurotic.MetadataSelector(file=self.temp_file,
                                             initial_selection=dataset)
        metadata.download('data_file')

        blk = neurotic.LoadAndPrepareData(metadata=metadata, lazy=True)
        video_jumps = neurotic.EstimateVideoJumpTimes(blk)
        del blk

        assert_array_almost_equal(
            np.array(video_jumps),
            np.array([[1.1998, 3], [4.6998, 3], [5.2998, 3]]),
            decimal=12,
            err_msg='EstimateVideoJumpTimes gave unexpected result')

if __name__ == '__main__':
    unittest.main()
