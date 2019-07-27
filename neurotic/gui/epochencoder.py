# -*- coding: utf-8 -*-
"""
The :mod:`neurotic.gui.epochencoder` module implements a subclass of
:class:`ephyviewer.datasource.epochs.WritableEpochSource`.

.. autoclass:: NeuroticWritableEpochSource
"""

import os
import shutil
import numpy as np
import pandas as pd
from ephyviewer import WritableEpochSource

class NeuroticWritableEpochSource(WritableEpochSource):
    """
    A subclass of :class:`ephyviewer.datasource.epochs.WritableEpochSource` for
    custom CSV column formatting and automatic file backup.
    """

    def __init__(self, filename, possible_labels, color_labels=None, channel_name='', backup=True):
        """
        Initialize a new NeuroticWritableEpochSource.
        """

        self.filename = filename
        self.backup = backup

        WritableEpochSource.__init__(self, epoch=None, possible_labels=possible_labels, color_labels=color_labels, channel_name=channel_name)

    def load(self):
        """
        Returns a dictionary containing the data for an epoch.

        Data is loaded from the CSV file if it exists; otherwise the superclass
        implementation in WritableEpochSource.load() is called to create an
        empty dictionary with the correct keys and types.

        The method returns a dictionary containing the loaded data in this form:

        { 'time': np.array, 'duration': np.array, 'label': np.array, 'name': string }
        """

        if os.path.exists(self.filename):
            # if file already exists, load previous epoch
            df = pd.read_csv(self.filename,  index_col=None, dtype={
                'Start (s)': 'float64',
                'End (s)':   'float64',
                'Type':      'U'})
            epoch = {'time':     df['Start (s)'].values,
                     'duration': df['End (s)'].values - df['Start (s)'].values,
                     'label':    df['Type'].values,
                     'name':     self.channel_name}
        else:
            # if file does NOT already exist, use superclass method for creating
            # an empty dictionary
            epoch = super().load()

        return epoch

    def save(self):
        """
        Save the epoch data to a CSV file, creating a backup first if the file
        already exists.
        """

        # if file already exists, make a backup copy first
        if self.backup and os.path.exists(self.filename):
            backup_filename = self.filename.split('.')
            backup_filename.insert(-1, 'bck')
            backup_filename = '.'.join(backup_filename)
            shutil.copy2(self.filename, backup_filename)

        df = pd.DataFrame()
        df['Start (s)'] = np.round(self.ep_times, 6)                   # round to nearest microsecond
        df['End (s)'] = np.round(self.ep_times + self.ep_durations, 6) # round to nearest microsecond
        df['Type'] = self.ep_labels
        df.sort_values(['Start (s)', 'End (s)', 'Type'], inplace=True)
        df.to_csv(self.filename, index=False)
