# -*- coding: utf-8 -*-
"""
Tools for working with Neo objects
"""

import re
import numpy as np
import pandas as pd
import neo
import elephant
from pylttb import lttb

class CausalAlphaKernel(elephant.kernels.AlphaKernel):
    """
    This modified version of elephant.kernels.AlphaKernel shifts time such that
    convolution of the kernel with spike trains (as in
    elephant.statistics.instantaneous_rate) results in alpha functions that
    begin rising at the spike time, not before. The entire area of the kernel
    comes after the spike, rather than half before and half after, as in
    AlphaKernel. Consequently, CausalAlphaKernel can be used in causal filters.

    Derived from:
    """
    __doc__ += elephant.kernels.AlphaKernel.__doc__

    def median_index(self, t):
        """
        In CausalAlphaKernel, "median_index" is a misnomer. Instead of returning
        the index into t that gives half area above and half below (median), it
        returns the index for the first non-negative time, which always
        corresponds to the start of the rise phase of the alpha function. This
        hack ensures that, when the kernel is convolved with a spike train, the
        entire alpha function is located to the right of each spike time.

        Overrides the following:
        """
        return np.nonzero(t >= 0)[0].min()
    median_index.__doc__ += elephant.kernels.AlphaKernel.median_index.__doc__

def DownsampleNeoSignal(sig, decimation_factor):
    """

    """

    assert sig.shape[1] == 1, 'Can only downsample single-channel signals'

    num_points = int(sig.shape[0] / decimation_factor)

    x_downsampled, y_downsampled = lttb(
        x=sig.times.magnitude,
        y=sig.magnitude[:, 0],
        threshold=num_points,
    )

    sig_downsampled = neo.IrregularlySampledSignal(
        times=x_downsampled,
        signal=y_downsampled,
        units=sig.units,
        time_units=sig.times.units,
    )
    return sig_downsampled

def NeoEpochToDataFrame(neo_epochs, exclude_epoch_encoder_epochs=False):
    """

    """

    dtypes = {
        'Start (s)':    float,
        'End (s)':      float,
        'Duration (s)': float,
        'Type':         str,
        'Label':        str,
    }
    columns = list(dtypes.keys())
    df = pd.DataFrame(columns=columns)
    for ep in neo_epochs:
        if not exclude_epoch_encoder_epochs or '(from epoch encoder file)' not in ep.labels:
            data = np.array([ep.times, ep.times+ep.durations, ep.durations, [ep.name]*len(ep), ep.labels]).T
            df = df.append(pd.DataFrame(data, columns=columns), ignore_index=True)
    return df.astype(dtype=dtypes).sort_values(['Start (s)', 'End (s)', 'Type', 'Label']).reset_index(drop=True)

def BehaviorsDataFrame(neo_epochs, behavior_query, subepoch_queries):
    """

    """

    # filter epochs to obtain the behaviors
    df = NeoEpochToDataFrame(neo_epochs)
    df = df.rename(columns={'Start (s)': 'Start', 'End (s)': 'End', 'Duration (s)': 'Duration'})
    df = df.query(behavior_query)
    df = df.rename(columns={'Start': 'Start (s)', 'End': 'End (s)', 'Duration': 'Duration (s)'})

    # add defaults for subepoch columns
    for col_prefix in subepoch_queries:
        df[col_prefix+' start (s)'] = np.nan
        df[col_prefix+' end (s)'] = np.nan
        df[col_prefix+' duration (s)'] = np.nan
        df[col_prefix+' type'] = ''
        df[col_prefix+' label'] = ''

    # for every behavior, identify other epochs that belong to it
    df2 = NeoEpochToDataFrame(neo_epochs)
    df2 = df2.rename(columns={'Start (s)': 'Start', 'End (s)': 'End', 'Duration (s)': 'Duration'})
    for i in df.index:

        # these variables are accessible within queries when the
        # @ symbol appears before their names, e.g. @behavior_start
        behavior_start    = df.loc[i, 'Start (s)']
        behavior_end      = df.loc[i, 'End (s)']
        behavior_duration = df.loc[i, 'Duration (s)']
        behavior_type     = df.loc[i, 'Type']
        behavior_label    = df.loc[i, 'Label']

        for col_prefix, query in subepoch_queries.items():
            df3 = df2.query(query)
            if len(df3) == 0:
                pass
            elif len(df3) == 1:
                matching_epoch = df3.iloc[0]
                df.loc[i, col_prefix+' start (s)'] = matching_epoch['Start']
                df.loc[i, col_prefix+' end (s)'] = matching_epoch['End']
                df.loc[i, col_prefix+' duration (s)'] = matching_epoch['Duration']
                df.loc[i, col_prefix+' type'] = matching_epoch['Type']
                df.loc[i, col_prefix+' label'] = matching_epoch['Label']
            else:
                raise Exception(f'More than one epoch was found for the behavior spanning [{behavior_start}, {behavior_end}] that matches this query: {query}')

    return df

def EstimateVideoJumpTimes(blk):
    """
    Estimate how much time to skip in video playback if AxoGraph was temporarily
    paused during data acquisition while the video continued to record. Returns
    a list of ordered pairs suitable for the video_jumps metadata parameter. The
    returned stop times are exact, but pause durations have only whole-second
    precision and should be manually refined by inspecting the video before
    using.
    """

    if 'notes' not in blk.annotations:
        return None
    else:

        # obtain approximate start and stop times according to AxoGraph notes
        note_start_times = np.array([0], dtype=np.int)
        note_stop_times = np.array([], dtype=np.int)
        for note_line in blk.annotations['notes'].split('\n'):
            m = re.match('\d\d\d: Start at (\d*) s', note_line)
            if m:
                note_start_times = np.append(note_start_times, int(m.group(1)))
            m = re.match('\d\d\d: Stop at (\d*) s', note_line)
            if m:
                note_stop_times = np.append(note_stop_times, int(m.group(1)))

        # calculate approximate pause durations
        pause_durations = note_start_times[1:]-note_stop_times[:-1]

        # obtain exact stop times (AxoGraph time, not video time)
        event_stop_times = np.array([], dtype=np.float)
        ev = blk.segments[0].events[0]
        for time, label in zip(ev.times, ev.labels):
            if label == 'Stop':
                event_stop_times = np.append(event_stop_times, time.magnitude)

        # pair stop times with pause durations
        video_jumps = []
        for t, dur in zip(event_stop_times[:-1], pause_durations):
            video_jumps.append([t, dur])

        return video_jumps
