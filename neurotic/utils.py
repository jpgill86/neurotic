# -*- coding: utf-8 -*-
"""
Tools for working with Neo objects
"""

import re
import numpy as np
import pandas as pd

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
        ev = next((ev for ev in blk.segments[0].events if ev.name == 'AxoGraph Tags'), None)
        if ev is not None:
            for time, label in zip(ev.times, ev.labels):
                if label == 'Stop':
                    event_stop_times = np.append(event_stop_times, time.magnitude)

        # pair stop times with pause durations
        video_jumps = []
        for t, dur in zip(event_stop_times[:-1], pause_durations):
            video_jumps.append([t, dur])

        return video_jumps
