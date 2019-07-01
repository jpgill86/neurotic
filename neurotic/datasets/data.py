# -*- coding: utf-8 -*-
"""
Import raw data, annotations, and spike sorting results as Neo objects
"""

import numpy as np
import pandas as pd
import quantities as pq
import elephant
import neo

from ..datasets.metadata import abs_path
from neo.test.generate_datasets import fake_neo

def LoadAndPrepareData(metadata, lazy=False, signal_group_mode='split-all', filter_events_from_epochs=False, fake_data_for_testing=False):
    """

    """

    # read in the electrophysiology data
    blk = ReadDataFile(metadata, lazy, signal_group_mode)
    # blk = CreateNeoBlockExample()

    # apply filters to signals if not using lazy loading of signals
    if not lazy:
        blk = ApplyFilters(metadata, blk)

    # copy events into epochs and vice versa
    epochs_from_events = [neo.Epoch(name=ev.name, times=ev.times, labels=ev.labels, durations=np.zeros_like(ev.times)) for ev in blk.segments[0].events]
    events_from_epochs = [neo.Event(name=ep.name, times=ep.times, labels=ep.labels) for ep in blk.segments[0].epochs]
    if not filter_events_from_epochs:
        blk.segments[0].epochs += epochs_from_events
    blk.segments[0].events += events_from_epochs

    # read in annotations
    annotations_dataframe = ReadAnnotationsFile(metadata)
    blk.segments[0].epochs += CreateNeoEpochsFromDataframe(annotations_dataframe, metadata, abs_path(metadata, 'annotations_file'), filter_events_from_epochs)
    blk.segments[0].events += CreateNeoEventsFromDataframe(annotations_dataframe, metadata, abs_path(metadata, 'annotations_file'))

    # read in epoch encoder file
    epoch_encoder_dataframe = ReadEpochEncoderFile(metadata)
    blk.segments[0].epochs += CreateNeoEpochsFromDataframe(epoch_encoder_dataframe, metadata, abs_path(metadata, 'epoch_encoder_file'), filter_events_from_epochs)
    blk.segments[0].events += CreateNeoEventsFromDataframe(epoch_encoder_dataframe, metadata, abs_path(metadata, 'epoch_encoder_file'))

    # classify spikes by amplitude if not using lazy loading of signals
    if not lazy:
        blk.segments[0].spiketrains += RunAmplitudeDiscriminators(metadata, blk)

    # read in spikes identified by spike sorting using tridesclous
    t_start = blk.segments[0].analogsignals[0].t_start
    t_stop = blk.segments[0].analogsignals[0].t_stop
    sampling_period = blk.segments[0].analogsignals[0].sampling_period
    spikes_dataframe = ReadSpikesFile(metadata, blk)
    blk.segments[0].spiketrains += CreateNeoSpikeTrainsFromDataframe(spikes_dataframe, metadata, t_start, t_stop, sampling_period)

    if fake_data_for_testing:
        # load fake data as a demo
        blk.segments[0].epochs += [fake_neo('Epoch') for _ in range(5)]
        blk.segments[0].events += [fake_neo('Event') for _ in range(5)]
        blk.segments[0].spiketrains += [fake_neo('SpikeTrain') for _ in range(5)]

    return blk

def ReadDataFile(metadata, lazy=False, signal_group_mode='split-all'):
    """

    """

    # read in the electrophysiology data
    # - signal_group_mode='split-all' ensures every channel gets its own
    #   AnalogSignal, which is important for indexing in EphyviewerConfigurator
    io = neo.io.get_io(abs_path(metadata, 'data_file'))
    blk = io.read_block(lazy=lazy, signal_group_mode=signal_group_mode)

    # load all proxy objects except analog signals
    if lazy:
        for i in range(len(blk.segments[0].epochs)):
            epoch = blk.segments[0].epochs[i]
            if hasattr(epoch, 'load'):
                blk.segments[0].epochs[i] = epoch.load()

        for i in range(len(blk.segments[0].events)):
            event = blk.segments[0].events[i]
            if hasattr(event, 'load'):
                blk.segments[0].events[i] = event.load()

        for i in range(len(blk.segments[0].spiketrains)):
            spiketrain = blk.segments[0].spiketrains[i]
            if hasattr(spiketrain, 'load'):
                blk.segments[0].spiketrains[i] = spiketrain.load()

    # convert byte labels to Unicode strings
    for epoch in blk.segments[0].epochs:
        epoch.labels = epoch.labels.astype('U')

    for event in blk.segments[0].events:
        event.labels = event.labels.astype('U')

    return blk

def ReadAnnotationsFile(metadata):
    """

    """

    if metadata['annotations_file'] is None:

        return None

    else:

        # data types for each column in the file
        dtypes = {
            'Start (s)': float,
            'End (s)':   float,
            'Type':      str,
            'Label':     str,
        }

        # parse the file and create a dataframe
        df = pd.read_csv(abs_path(metadata, 'annotations_file'), dtype = dtypes)

        # increment row labels by 2 so they match the source file
        # which is 1-indexed and has a header
        df.index += 2

        # discard entries with missing or negative start times
        bad_start = df['Start (s)'].isnull() | (df['Start (s)'] < 0)
        if bad_start.any():
            print('NOTE: These rows will be discarded because their Start times are missing or negative:')
            print(df[bad_start])
            df = df[~bad_start]

        # discard entries with end time preceding start time
        bad_end = df['End (s)'] < df['Start (s)']
        if bad_end.any():
            print('NOTE: These rows will be discarded because their End times precede their Start times:')
            print(df[bad_end])
            df = df[~bad_end]

        # compute durations
        df.insert(
            column = 'Duration (s)',
            value = df['End (s)'] - df['Start (s)'],
            loc = 2, # insert after 'End (s)'
        )

        # replace some NaNs
        df.fillna({
            'Duration (s)': 0,
            'Type': 'Other',
            'Label': '',
        }, inplace = True)

        # sort entries by time
        df.sort_values([
            'Start (s)',
            'Duration (s)',
        ], inplace = True)

        # return the dataframe
        return df

def ReadEpochEncoderFile(metadata):
    """

    """

    if metadata['epoch_encoder_file'] is None:

        return None

    else:

        # data types for each column in the file
        dtypes = {
            'Start (s)': float,
            'End (s)':   float,
            'Type':      str,
        }

        # parse the file and create a dataframe
        df = pd.read_csv(abs_path(metadata, 'epoch_encoder_file'), dtype = dtypes)

        # increment row labels by 2 so they match the source file
        # which is 1-indexed and has a header
        df.index += 2

        # discard entries with missing or negative start times
        bad_start = df['Start (s)'].isnull() | (df['Start (s)'] < 0)
        if bad_start.any():
            print('NOTE: These rows will be discarded because their Start times are missing or negative:')
            print(df[bad_start])
            df = df[~bad_start]

        # discard entries with end time preceding start time
        bad_end = df['End (s)'] < df['Start (s)']
        if bad_end.any():
            print('NOTE: These rows will be discarded because their End times precede their Start times:')
            print(df[bad_end])
            df = df[~bad_end]

        # compute durations
        df.insert(
            column = 'Duration (s)',
            value = df['End (s)'] - df['Start (s)'],
            loc = 2, # insert after 'End (s)'
        )

        # replace some NaNs
        df.fillna({
            'Duration (s)': 0,
            'Type': 'Other',
        }, inplace = True)

        # sort entries by time
        df.sort_values([
            'Start (s)',
            'Duration (s)',
        ], inplace = True)

        # add 'Label' column to indicate where these epochs came from
        df.insert(
            column = 'Label',
            value = '(from epoch encoder file)',
            loc = 4, # insert after 'Type'
        )

        # return the dataframe
        return df

def ReadSpikesFile(metadata, blk):
    """
    Read in spikes identified by spike sorting with tridesclous.
    """

    if metadata['tridesclous_file'] is None or metadata['tridesclous_channels'] is None:

        return None

    else:

        # parse the file and create a dataframe
        df = pd.read_csv(abs_path(metadata, 'tridesclous_file'), names = ['index', 'label'])

        # drop clusters with negative labels
        df = df[df['label'] >= 0]

        if metadata['tridesclous_merge']:
            # merge some clusters and drop all others
            new_labels = []
            for clusters_to_merge in metadata['tridesclous_merge']:
                new_label = clusters_to_merge[0]
                new_labels.append(new_label)
                df.loc[df['label'].isin(clusters_to_merge), 'label'] = new_label
            df = df[df['label'].isin(new_labels)]

        # return the dataframe
        return df

def CreateNeoEpochsFromDataframe(dataframe, metadata, file_origin, filter_events_from_epochs=False):
    """

    """

    epochs_list = []

    if dataframe is not None:

        if filter_events_from_epochs:
            # keep only rows with a positive duration
            dataframe = dataframe[dataframe['Duration (s)'] > 0]

        # group epochs by type
        for type_name, df in dataframe.groupby('Type'):

            # create a Neo Epoch for each type
            epoch = neo.Epoch(
                name = type_name,
                file_origin = file_origin,
                times = df['Start (s)'].values * pq.s,
                durations = df['Duration (s)'].values * pq.s,
                labels = df['Label'].values,
            )

            epochs_list.append(epoch)

    # return the list of Neo Epochs
    return epochs_list

def CreateNeoEventsFromDataframe(dataframe, metadata, file_origin):
    """

    """

    events_list = []

    if dataframe is not None:

        # group events by type
        for type_name, df in dataframe.groupby('Type'):

            # create a Neo Event for each type
            event = neo.Event(
                name = type_name,
                file_origin = file_origin,
                times = df['Start (s)'].values * pq.s,
                labels = df['Label'].values,
            )

            events_list.append(event)

    # return the list of Neo Events
    return events_list

def CreateNeoSpikeTrainsFromDataframe(dataframe, metadata, t_start, t_stop, sampling_period):
    """

    """

    spiketrain_list = []

    if dataframe is not None:

        # group spikes by cluster label
        for spike_label, df in dataframe.groupby('label'):

            # look up the channels that this unit was found on
            channels = metadata['tridesclous_channels'][spike_label]

            # create a Neo SpikeTrain for each cluster label
            st = neo.SpikeTrain(
                name = str(spike_label),
                file_origin = abs_path(metadata, 'tridesclous_file'),
                channels = channels, # custom annotation
                amplitude = None,    # custom annotation
                times = t_start + sampling_period * df['index'].values,
                t_start = t_start,
                t_stop = t_stop,
            )

            spiketrain_list.append(st)

    return spiketrain_list

def ApplyFilters(metadata, blk):
    """

    """

    if metadata['filters'] is not None:

        signalNameToIndex = {sig.name:i for i, sig in enumerate(blk.segments[0].analogsignals)}

        for sig_filter in metadata['filters']:

            index = signalNameToIndex.get(sig_filter['channel'], None)
            if index is None:

                print('Warning: skipping filter with channel name {} because channel was not found!'.format(sig_filter['channel']))

            else:

                high = sig_filter.get('highpass', None)
                low  = sig_filter.get('lowpass',  None)
                if high:
                    high *= pq.Hz
                if low:
                    low  *= pq.Hz
                blk.segments[0].analogsignals[index] = elephant.signal_processing.butter(  # may raise a FutureWarning
                    signal = blk.segments[0].analogsignals[index],
                    highpass_freq = high,
                    lowpass_freq  = low,
                )

    return blk

def RunAmplitudeDiscriminators(metadata, blk):
    """

    """

    spiketrain_list = []

    if metadata['amplitude_discriminators'] is not None:

        signalNameToIndex = {sig.name:i for i, sig in enumerate(blk.segments[0].analogsignals)}
        epochs = blk.segments[0].epochs

        # classify spikes by amplitude
        for discriminator in metadata['amplitude_discriminators']:

            index = signalNameToIndex.get(discriminator['channel'], None)
            if index is None:

                print('Warning: skipping amplitude discriminator with channel name {} because channel was not found!'.format(discriminator['channel']))

            else:

                sig = blk.segments[0].analogsignals[index]
                st = DetectSpikes(sig, discriminator, epochs)
                spiketrain_list.append(st)

    return spiketrain_list


def DetectSpikes(sig, discriminator, epochs):
    """

    """

    assert sig.name == discriminator['channel'], 'sig name "{}" does not match amplitude discriminator channel "{}"'.format(sig.name, discriminator['channel'])

    min_threshold = min(discriminator['amplitude'])
    max_threshold = max(discriminator['amplitude'])
    if min_threshold >= 0 and max_threshold > 0:
        sign = 'above'
    elif min_threshold < 0 and max_threshold <= 0:
        sign = 'below'
    else:
        raise ValueError('amplitude discriminator must have two nonnegative thresholds or two nonpositive thresholds: {}'.format(discriminator))

    spikes_crossing_min = elephant.spike_train_generation.peak_detection(sig, min_threshold*pq.uV, sign, 'raw')
    spikes_crossing_max = elephant.spike_train_generation.peak_detection(sig, max_threshold*pq.uV, sign, 'raw')
    if sign == 'above':
        spikes_between_min_and_max = np.setdiff1d(spikes_crossing_min, spikes_crossing_max)
    elif sign == 'below':
        spikes_between_min_and_max = np.setdiff1d(spikes_crossing_max, spikes_crossing_min)
    else:
        raise ValueError('sign should be "above" or "below": {}'.format(sign))

    st = neo.SpikeTrain(
        name = discriminator['name'],
        channels = [discriminator['channel']],  # custom annotation
        amplitude = discriminator['amplitude'], # custom annotation
        times = spikes_between_min_and_max * pq.s,
        t_start = sig.t_start,
        t_stop  = sig.t_stop,
    )

    if 'epoch' in discriminator:

        time_masks = []
        if isinstance(discriminator['epoch'], str):
            # search for matching epochs
            ep = next((ep for ep in epochs if ep.name == discriminator['epoch']), None)
            if ep is not None:
                # select spike times that fall within each epoch
                for t_start, duration in zip(ep.times, ep.durations):
                    t_stop = t_start + duration
                    time_masks.append((t_start <= st) & (st < t_stop))
            else:
                # no matching epochs found
                time_masks.append([False] * len(st))
        else:
            # may eventually implement lists of ordered pairs, but
            # for now raise an error
            raise ValueError('amplitude discriminator epoch could not be handled: {}'.format(discriminator['epoch']))

        # select the subset of spikes that fall within the epoch
        # windows
        st = st[np.any(time_masks, axis=0)]

    return st
