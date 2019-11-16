# -*- coding: utf-8 -*-
"""
The :mod:`neurotic.elephant_tools` module contains functions copied from the
elephant package, which are included for convenience and to eliminate
dependency on that package.

This module and the functions it contains are not intended to be part of
neurotic's public API, so all function names begin with underscores. This
module may be removed at a future date.

elephant is licensed under BSD-3-Clause:

Copyright (c) 2014-2019, Elephant authors and contributors All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
* list of conditions and the following disclaimer. Redistributions in binary
* form must reproduce the above copyright notice, this list of conditions and
* the following disclaimer in the documentation and/or other materials provided
* with the distribution. Neither the names of the copyright holders nor the
* names of the contributors may be used to endorse or promote products derived
* from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import numpy as np
import scipy.signal
import quantities as pq
from quantities import ms, mV, Hz, Quantity, dimensionless
import neo
from neo import SpikeTrain


def _butter(signal, highpass_freq=None, lowpass_freq=None, order=4,
            filter_function='filtfilt', fs=1.0, axis=-1):
    """
    Butterworth filtering function for neo.AnalogSignal. Filter type is
    determined according to how values of `highpass_freq` and `lowpass_freq`
    are given (see Parameters section for details).

    Parameters
    ----------
    signal : AnalogSignal or Quantity array or NumPy ndarray
        Time series data to be filtered. When given as Quantity array or NumPy
        ndarray, the sampling frequency should be given through the keyword
        argument `fs`.
    highpass_freq, lowpass_freq : Quantity or float
        High-pass and low-pass cut-off frequencies, respectively. When given as
        float, the given value is taken as frequency in Hz.
        Filter type is determined depending on values of these arguments:
            * highpass_freq only (lowpass_freq = None):    highpass filter
            * lowpass_freq only (highpass_freq = None):    lowpass filter
            * highpass_freq < lowpass_freq:    bandpass filter
            * highpass_freq > lowpass_freq:    bandstop filter
    order : int
        Order of Butterworth filter. Default is 4.
    filter_function : string
        Filtering function to be used. Available filters:
            * 'filtfilt': `scipy.signal.filtfilt()`;
            * 'lfilter': `scipy.signal.lfilter()`;
            * 'sosfiltfilt': `scipy.signal.sosfiltfilt()`.
        In most applications 'filtfilt' should be used, because it doesn't
        bring about phase shift due to filtering. For numerically stable
        filtering, in particular higher order filters, use 'sosfiltfilt'
        (see issue
        https://github.com/NeuralEnsemble/elephant/issues/220).
        Default is 'filtfilt'.
    fs : Quantity or float
        The sampling frequency of the input time series. When given as float,
        its value is taken as frequency in Hz. When the input is given as neo
        AnalogSignal, its attribute is used to specify the sampling
        frequency and this parameter is ignored. Default is 1.0.
    axis : int
        Axis along which filter is applied. Default is -1.

    Returns
    -------
    filtered_signal : AnalogSignal or Quantity array or NumPy ndarray
        Filtered input data. The shape and type is identical to those of the
        input.

    Raises
    ------
    ValueError
        If `filter_function` is not one of 'lfilter', 'filtfilt',
        or 'sosfiltfilt'.
        When both `highpass_freq` and `lowpass_freq` are None.

    """
    available_filters = 'lfilter', 'filtfilt', 'sosfiltfilt'
    if filter_function not in available_filters:
        raise ValueError("Invalid `filter_function`: {filter_function}. "
                         "Available filters: {available_filters}".format(
                          filter_function=filter_function,
                          available_filters=available_filters))
    # design filter
    if hasattr(signal, 'sampling_rate'):
        fs = signal.sampling_rate.rescale(pq.Hz).magnitude
    if isinstance(highpass_freq, pq.quantity.Quantity):
        highpass_freq = highpass_freq.rescale(pq.Hz).magnitude
    if isinstance(lowpass_freq, pq.quantity.Quantity):
        lowpass_freq = lowpass_freq.rescale(pq.Hz).magnitude
    Fn = fs / 2.
    # filter type is determined according to the values of cut-off
    # frequencies
    if lowpass_freq and highpass_freq:
        if highpass_freq < lowpass_freq:
            Wn = (highpass_freq / Fn, lowpass_freq / Fn)
            btype = 'bandpass'
        else:
            Wn = (lowpass_freq / Fn, highpass_freq / Fn)
            btype = 'bandstop'
    elif lowpass_freq:
        Wn = lowpass_freq / Fn
        btype = 'lowpass'
    elif highpass_freq:
        Wn = highpass_freq / Fn
        btype = 'highpass'
    else:
        raise ValueError(
            "Either highpass_freq or lowpass_freq must be given"
        )
    if filter_function == 'sosfiltfilt':
        output = 'sos'
    else:
        output = 'ba'
    designed_filter = scipy.signal.butter(order, Wn, btype=btype,
                                          output=output)

    # When the input is AnalogSignal, the axis for time index (i.e. the
    # first axis) needs to be rolled to the last
    data = np.asarray(signal)
    if isinstance(signal, neo.AnalogSignal):
        data = np.rollaxis(data, 0, len(data.shape))

    # apply filter
    if filter_function == 'lfilter':
        b, a = designed_filter
        filtered_data = scipy.signal.lfilter(b=b, a=a, x=data, axis=axis)
    elif filter_function == 'filtfilt':
        b, a = designed_filter
        filtered_data = scipy.signal.filtfilt(b=b, a=a, x=data, axis=axis)
    else:
        filtered_data = scipy.signal.sosfiltfilt(sos=designed_filter,
                                                 x=data, axis=axis)

    if isinstance(signal, neo.AnalogSignal):
        filtered_data = np.rollaxis(filtered_data, -1, 0)
        return signal.duplicate_with_new_data(filtered_data)
    elif isinstance(signal, pq.quantity.Quantity):
        return filtered_data * signal.units
    else:
        return filtered_data

def _peak_detection(signal, threshold=0.0 * mV, sign='above', format=None):
    """
    Return the peak times for all events that cross threshold.
    Usually used for extracting spike times from a membrane potential.
    Similar to spike_train_generation.threshold_detection.

    Parameters
    ----------
    signal : neo AnalogSignal object
        'signal' is an analog signal.
    threshold : A quantity, e.g. in mV
        'threshold' contains a value that must be reached
        for an event to be detected.
    sign : 'above' or 'below'
        'sign' determines whether to count thresholding crossings that
        cross above or below the threshold. Default: 'above'.
    format : None or 'raw'
        Whether to return as SpikeTrain (None) or as a plain array
        of times ('raw'). Default: None.

    Returns
    -------
    result_st : neo SpikeTrain object
        'result_st' contains the spike times of each of the events
        (spikes) extracted from the signal.
    """
    assert threshold is not None, "A threshold must be provided"

    if sign == 'above':
        cutout = np.where(signal > threshold)[0]
        peak_func = np.argmax
    elif sign == 'below':
        cutout = np.where(signal < threshold)[0]
        peak_func = np.argmin
    else:
        raise ValueError("sign must be 'above' or 'below'")

    if len(cutout) <= 0:
        events_base = np.zeros(0)
    else:
        # Select thr crossings lasting at least 2 dtps, np.diff(cutout) > 2
        # This avoids empty slices
        border_start = np.where(np.diff(cutout) > 1)[0]
        border_end = border_start + 1
        borders = np.concatenate((border_start, border_end))
        borders = np.append(0, borders)
        borders = np.append(borders, len(cutout)-1)
        borders = np.sort(borders)
        true_borders = cutout[borders]
        right_borders = true_borders[1::2] + 1
        true_borders = np.sort(np.append(true_borders[0::2], right_borders))

        # Workaround for bug that occurs when signal goes below thr for 1 dtp,
        # Workaround eliminates empy slices from np. split
        backward_mask = np.absolute(np.ediff1d(true_borders, to_begin=1)) > 0
        forward_mask = np.absolute(np.ediff1d(true_borders[::-1],
                                              to_begin=1)[::-1]) > 0
        true_borders = true_borders[backward_mask * forward_mask]
        split_signal = np.split(np.array(signal), true_borders)[1::2]

        maxima_idc_split = np.array([peak_func(x) for x in split_signal])

        max_idc = maxima_idc_split + true_borders[0::2]

        events = signal.times[max_idc]
        events_base = events.magnitude

        if events_base is None:
            # This occurs in some Python 3 builds due to some
            # bug in quantities.
            events_base = np.array([event.magnitude for event in events])  # Workaround
    if format is None:
        result_st = SpikeTrain(events_base, units=signal.times.units,
                               t_start=signal.t_start, t_stop=signal.t_stop)
    elif 'raw':
        result_st = events_base
    else:
        raise ValueError("Format argument must be None or 'raw'")

    return result_st

def _rauc(signal, baseline=None, bin_duration=None, t_start=None, t_stop=None):
    '''
    Calculate the rectified area under the curve (RAUC) for an AnalogSignal.

    The signal is optionally divided into bins with duration `bin_duration`,
    and the rectified signal (absolute value) is integrated within each bin to
    find the area under the curve. The mean or median of the signal or an
    arbitrary baseline may optionally be subtracted before rectification. If
    the number of bins is 1 (default), a single value is returned for each
    channel in the input signal. Otherwise, an AnalogSignal containing the
    values for each bin is returned along with the times of the centers of the
    bins.

    Parameters
    ----------
    signal : neo.AnalogSignal
        The signal to integrate. If `signal` contains more than one channel,
        each is integrated separately.
    bin_duration : quantities.Quantity
        The length of time that each integration should span. If None, there
        will be only one bin spanning the entire signal duration. If
        `bin_duration` does not divide evenly into the signal duration, the end
        of the signal is padded with zeros to accomodate the final,
        overextending bin.
        Default: None
    baseline : string or quantities.Quantity
        A factor to subtract from the signal before rectification. If `'mean'`
        or `'median'`, the mean or median value of the entire signal is
        subtracted on a channel-by-channel basis.
        Default: None
    t_start, t_stop : quantities.Quantity
        Times to start and end the algorithm. The signal is cropped using
        `signal.time_slice(t_start, t_stop)` after baseline removal. Useful if
        you want the RAUC for a short section of the signal but want the
        mean or median calculation (`baseline='mean'` or `baseline='median'`)
        to use the entire signal for better baseline estimation.
        Default: None

    Returns
    -------
    quantities.Quantity or neo.AnalogSignal
        If the number of bins is 1, the returned object is a scalar or
        vector Quantity containing a single RAUC value for each channel.
        Otherwise, the returned object is an AnalogSignal containing the
        RAUC(s) for each bin stored as a sample, with times corresponding to
        the center of each bin. The output signal will have the same number
        of channels as the input signal.

    Raises
    ------
    TypeError
        If the input signal is not a neo.AnalogSignal.
    TypeError
        If `bin_duration` is not None or a Quantity.
    TypeError
        If `baseline` is not None, `'mean'`, `'median'`, or a Quantity.
    '''

    if not isinstance(signal, neo.AnalogSignal):
        raise TypeError('Input signal is not a neo.AnalogSignal!')

    if baseline is None:
        pass
    elif baseline == 'mean':
        # subtract mean from each channel
        signal = signal - signal.mean(axis=0)
    elif baseline == 'median':
        # subtract median from each channel
        signal = signal - np.median(signal.as_quantity(), axis=0)
    elif isinstance(baseline, pq.Quantity):
        # subtract arbitrary baseline
        signal = signal - baseline
    else:
        raise TypeError(
            'baseline must be None, \'mean\', \'median\', '
            'or a Quantity: {}'.format(baseline))

    # slice the signal after subtracting baseline
    signal = signal.time_slice(t_start, t_stop)

    if bin_duration is not None:
        # from bin duration, determine samples per bin and number of bins
        if isinstance(bin_duration, pq.Quantity):
            samples_per_bin = int(np.round(
                bin_duration.rescale('s')/signal.sampling_period.rescale('s')))
            n_bins = int(np.ceil(signal.shape[0]/samples_per_bin))
        else:
            raise TypeError(
                'bin_duration must be a Quantity: {}'.format(bin_duration))
    else:
        # all samples in one bin
        samples_per_bin = signal.shape[0]
        n_bins = 1

    # store the actual bin duration
    bin_duration = samples_per_bin * signal.sampling_period

    # reshape into equal size bins, padding the end with zeros if necessary
    n_channels = signal.shape[1]
    sig_binned = signal.as_quantity().copy()
    sig_binned.resize(n_bins * samples_per_bin, n_channels, refcheck=False)
    sig_binned = sig_binned.reshape(n_bins, samples_per_bin, n_channels)

    # rectify and integrate over each bin
    rauc = np.trapz(np.abs(sig_binned), dx=signal.sampling_period, axis=1)

    if n_bins == 1:
        # return a single value for each channel
        return rauc.squeeze()

    else:
        # return an AnalogSignal with times corresponding to center of each bin
        rauc_sig = neo.AnalogSignal(
            rauc,
            t_start=signal.t_start.rescale(bin_duration.units)+bin_duration/2,
            sampling_period=bin_duration)
        return rauc_sig
