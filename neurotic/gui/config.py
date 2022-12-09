# -*- coding: utf-8 -*-
"""
The :mod:`neurotic.gui.config` module implements a class for configuring and
launching ephyviewer for a loaded dataset.

.. autoclass:: EphyviewerConfigurator
   :members:
"""

import re

import numpy as np
import pandas as pd
import quantities as pq
import neo
import ephyviewer

from ..datasets.metadata import _abs_path
from ..gui.epochencoder import NeuroticWritableEpochSource

import logging
logger = logging.getLogger(__name__)


# raise the threshold for PyAV messages printed to the console from
# warning to critical
logging.getLogger('libav').setLevel(logging.CRITICAL)


pq.mN = pq.UnitQuantity('millinewton', pq.N/1e3, symbol = 'mN');  # define millinewton


available_themes = ['light', 'dark', 'original', 'printer-friendly']
available_ui_scales = ['tiny', 'small', 'medium', 'large', 'huge']


class EphyviewerConfigurator():
    """
    A class for launching ephyviewer for a dataset with configurable viewers.

    At initialization, invalid viewers are automatically disabled (e.g., the
    video viewer is disabled if ``video_file`` is not given in ``metadata``).
    Viewers can be hidden or shown before launch using the built-in methods.
    Valid viewer names are:

        * ``traces``
        * ``traces_rauc``
        * ``freqs``
        * ``spike_trains``
        * ``traces_rates``
        * ``epochs``
        * ``epoch_encoder``
        * ``video``
        * ``event_list``
        * ``data_frame``

    :meth:`launch_ephyviewer` is provided for starting a new Qt app and
    launching the ephyviewer main window all at once.
    :meth:`create_ephyviewer_window` generates just the ephyviewer window
    and should be used if there is already a Qt app running.
    """

    def __init__(self, metadata, blk, lazy = False):
        """
        Initialize a new EphyviewerConfigurator.
        """

        self.metadata = metadata
        self.blk = blk
        self.lazy = lazy

        self.viewer_settings = {
            'traces':        {'show': True, 'disabled': False, 'reason': ''},
            'traces_rauc':   {'show': False, 'disabled': False, 'reason': ''},
            'freqs':         {'show': False, 'disabled': True, 'reason': 'Disabled because feature is experimental and computationally expensive'},
            'spike_trains':  {'show': True, 'disabled': False, 'reason': ''},
            'traces_rates':  {'show': True, 'disabled': False, 'reason': ''},
            'epochs':        {'show': True, 'disabled': False, 'reason': ''},
            'epoch_encoder': {'show': True, 'disabled': False, 'reason': ''},
            'video':         {'show': True, 'disabled': False, 'reason': ''},
            'event_list':    {'show': True, 'disabled': False, 'reason': ''},
            'data_frame':    {'show': False, 'disabled': False, 'reason': ''},
        }

        self.themes = {}
        self.themes['original'] = None # special keyword to use ephyviewer's defaults
        self.themes['light'] = {
            'cmap': 'Dark2', # dark traces
            'background_color': '#F0F0F0', # light gray
            'vline_color': '#000000AA', # transparent black
            'label_fill_color': '#DDDDDDDD', # transparent light gray
        }
        self.themes['dark'] = {
            'cmap': 'Accent', # light traces
            'background_color': 'k', # black
            'vline_color': '#FFFFFFAA', # transparent white
            'label_fill_color': '#222222DD', # transparent dark gray
        }
        self.themes['printer-friendly'] = {
            'cmap': 'Dark2', # dark traces
            'background_color': '#FFFFFF', # white
            'vline_color': '#000000AA', # transparent black
            'label_fill_color': '#DDDDDDDD', # transparent light gray
        }

        # hide and disable viewers for which inputs are missing
        if not self.blk.segments[0].analogsignals:
            self.viewer_settings['traces']['show'] = False
            self.viewer_settings['traces']['disabled'] = True
            self.viewer_settings['traces']['reason'] = 'Cannot enable because there are no signals'
        if not [sig.annotations['rauc_sig'] for sig in blk.segments[0].analogsignals if 'rauc_sig' in sig.annotations]:
            self.viewer_settings['traces_rauc']['show'] = False
            self.viewer_settings['traces_rauc']['disabled'] = True
            self.viewer_settings['traces_rauc']['reason'] = 'Cannot enable because there are no RAUC signals'
        if not self.blk.segments[0].spiketrains:
            self.viewer_settings['spike_trains']['show'] = False
            self.viewer_settings['spike_trains']['disabled'] = True
            self.viewer_settings['spike_trains']['reason'] = 'Cannot enable because there are no spike trains'
        if not [st.annotations['firing_rate_sig'] for st in blk.segments[0].spiketrains if 'firing_rate_sig' in st.annotations]:
            self.viewer_settings['traces_rates']['show'] = False
            self.viewer_settings['traces_rates']['disabled'] = True
            self.viewer_settings['traces_rates']['reason'] = 'Cannot enable because there are no firing rate signals'
        if not [ep for ep in self.blk.segments[0].epochs if ep.size > 0 and '(from epoch encoder file)' not in ep.labels]:
            self.viewer_settings['epochs']['show'] = False
            self.viewer_settings['epochs']['disabled'] = True
            self.viewer_settings['epochs']['reason'] = 'Cannot enable because there are no read-only epochs'
            self.viewer_settings['data_frame']['show'] = False
            self.viewer_settings['data_frame']['disabled'] = True
            self.viewer_settings['data_frame']['reason'] = 'Cannot enable because there are no read-only epochs'
            if not [ev for ev in self.blk.segments[0].events if ev.size > 0]:
                self.viewer_settings['event_list']['show'] = False
                self.viewer_settings['event_list']['disabled'] = True
                self.viewer_settings['event_list']['reason'] = 'Cannot enable because there are no read-only epochs or events'
        if not self.metadata.get('epoch_encoder_file', None):
            self.viewer_settings['epoch_encoder']['show'] = False
            self.viewer_settings['epoch_encoder']['disabled'] = True
            self.viewer_settings['epoch_encoder']['reason'] = 'Cannot enable because epoch_encoder_file is not set'
        if not ephyviewer.HAVE_AV:
            self.viewer_settings['video']['show'] = False
            self.viewer_settings['video']['disabled'] = True
            self.viewer_settings['video']['reason'] = 'Cannot enable because PyAV is not installed'
        if not self.metadata.get('video_file', None):
            self.viewer_settings['video']['show'] = False
            self.viewer_settings['video']['disabled'] = True
            self.viewer_settings['video']['reason'] = 'Cannot enable because video_file is not set'
        if not ephyviewer.HAVE_AV and self.metadata.get('video_file', None):
            logger.warning('Ignoring video_file because PyAV is not installed')

        # warn about potential video sync problems
        if metadata.get('video_file', None) is not None and metadata.get('video_offset', None) is None:
            logger.warning('Your video will likely be out of sync with your '
                           'data because video_offset is unspecified! '
                           'Consider adding it to your metadata.')
        if metadata.get('video_file', None) is not None and metadata.get('video_jumps', None) is None:
            approx_video_jumps = _estimate_video_jump_times(blk)
            if approx_video_jumps:
                approx_video_jumps_recommendation = '    video_jumps:\n' + \
                    '\n'.join([f'        - [{t}, {dur}]' for t, dur in approx_video_jumps])
                logger.warning('It seems that AxoGraph was paused at least '
                               'once during data acquisition, but video_jumps '
                               'is unspecified. This will cause your video '
                               'and data to get out of sync. Consider adding '
                               'the following to your metadata:'
                               f'\n{approx_video_jumps_recommendation}\n'
                               'Each ordered pair specifies the timing of a '
                               'pause and approximately how long the pause '
                               'lasted in seconds. The pause durations are '
                               'only rough estimates +/- a second! You should '
                               'refine them by inspecting the video to make '
                               'sure your sync is accurate!')

    def is_enabled(self, name):
        """
        Return whether the viewer ``name`` is enabled.
        """
        if name in self.viewer_settings:
            return not self.viewer_settings[name]['disabled']
        else:
            return False

    def enable(self, name):
        """
        Enable the viewer ``name``.
        """
        if name in self.viewer_settings:
            self.viewer_settings[name]['disabled'] = False

    def disable(self, name):
        """
        Disable the viewer ``name``.
        """
        if name in self.viewer_settings:
            self.viewer_settings[name]['disabled'] = True

    def is_shown(self, name):
        """
        Return whether the viewer ``name`` is shown.
        """
        if name in self.viewer_settings:
            return self.viewer_settings[name]['show']
        else:
            return False

    def show(self, name):
        """
        Show the viewer ``name``.
        """
        if name in self.viewer_settings:
            if not self.viewer_settings[name]['disabled']:
                self.viewer_settings[name]['show'] = True
            else:
                logger.warning(self.viewer_settings[name]['reason'])
        else:
            logger.error(f'"{name}" is not a viewer in viewer_settings')

    def hide(self, name):
        """
        Hide the viewer ``name``.
        """
        if name in self.viewer_settings:
            self.viewer_settings[name]['show'] = False
        else:
            logger.error(f'"{name}" is not a viewer in viewer_settings')

    def show_all(self):
        """
        Show all viewers.
        """
        for name in self.viewer_settings:
            if not self.viewer_settings[name]['disabled']:
                self.show(name)

    def hide_all(self):
        """
        Hide all viewers.
        """
        for name in self.viewer_settings:
            self.hide(name)

    def launch_ephyviewer(self, theme='light', ui_scale='medium', support_increased_line_width=False, show_datetime=False, datetime_format='%Y-%m-%d %H:%M:%S'):
        """
        Start a Qt app and create an ephyviewer window.
        """

        app = ephyviewer.mkQApp()
        win = self.create_ephyviewer_window(theme=theme, ui_scale=ui_scale, support_increased_line_width=support_increased_line_width, show_datetime=show_datetime, datetime_format=datetime_format)
        win.show()
        app.exec_()

    def create_ephyviewer_window(self, theme='light', ui_scale='medium', support_increased_line_width=False, show_datetime=False, datetime_format='%Y-%m-%d %H:%M:%S'):
        """
        Load data into each ephyviewer viewer and return the main window.
        """

        ########################################################################
        # DATA SOURCES

        seg = self.blk.segments[0]
        sigs = seg.analogsignals

        sources = {'signal': [], 'epoch': [], 'event': [], 'spike': []}
        sources['epoch'].append(ephyviewer.NeoEpochSource(seg.epochs))
        sources['event'].append(ephyviewer.NeoEventSource(seg.events))
        sources['spike'].append(ephyviewer.NeoSpikeTrainSource(seg.spiketrains))

        # filter epoch encoder data out of read-only epoch and event lists
        # so they are not presented multiple times, and remove empty channels
        sources['epoch'][0].all = [ep for ep in sources['epoch'][0].all if len(ep['time']) > 0 and '(from epoch encoder file)' not in ep['label']]
        sources['event'][0].all = [ev for ev in sources['event'][0].all if len(ev['time']) > 0 and '(from epoch encoder file)' not in ev['label']]

        ########################################################################
        # WINDOW

        # optionally display the real-world date and time
        if show_datetime and self.blk.rec_datetime is not None:
            show_label_datetime = True
            datetime0 = self.blk.rec_datetime
        else:
            show_label_datetime = False
            datetime0 = None

        # create a window that will be populated with viewers
        win = ephyviewer.MainViewer(
            # settings_name='test2', # remember settings (e.g. xsize) between sessions
            show_auto_scale = True,
            global_xsize_zoom = True,
            play_interval = 0.1, # refresh period in seconds
            show_label_datetime = show_label_datetime,
            datetime0 = datetime0,
            datetime_format = datetime_format,
        )
        win.setWindowTitle(self.metadata.get('key', 'neurotic'))
        win.setWindowIcon(ephyviewer.QT.QIcon(':/neurotic-logo-150.png'))

        # delete on close so that memory and file resources are released
        win.setAttribute(ephyviewer.QT.WA_DeleteOnClose, True)

        # determine ui_scale parameters
        default_font_size = ephyviewer.QT.QFont().pointSize()
        ui_scales = {
            'tiny':   {'app_font_size': default_font_size-4, 'channel_label_size': default_font_size-4, 'scatter_size':  4},
            'small':  {'app_font_size': default_font_size-2, 'channel_label_size': default_font_size-2, 'scatter_size':  6},
            'medium': {'app_font_size': default_font_size,   'channel_label_size': default_font_size,   'scatter_size':  8},
            'large':  {'app_font_size': default_font_size+4, 'channel_label_size': default_font_size+4, 'scatter_size': 10},
            'huge':   {'app_font_size': default_font_size+8, 'channel_label_size': default_font_size+8, 'scatter_size': 12},
        }

        # set the font size for most text
        font = win.font()
        font.setPointSize(ui_scales[ui_scale]['app_font_size'])
        win.setFont(font)

        ########################################################################
        # COLORS

        # colors for signals given explicitly in plots, used for raw signals
        # and RAUC
        sig_colors = {}
        if self.metadata.get('plots', None) is not None:
            sig_colors = {p['channel']: p['color'] for p in self.metadata['plots'] if 'color' in p}

        # colors for units given explicitly in amplitude_discriminators, used
        # for scatter markers, spike trains, and burst epochs
        unit_colors = {}
        if self.metadata.get('amplitude_discriminators', None) is not None:
            unit_colors = {d['name']: d['color'] for d in self.metadata['amplitude_discriminators'] if 'color' in d}

        ########################################################################
        # TRACES WITH SCATTER PLOTS

        _set_defaults_for_plots(self.metadata, self.blk)

        if self.is_shown('traces') and self.metadata['plots']:

            lazy_load_signals = False
            if self.lazy:
                # check whether blk contains a rawio, which would have been put
                # there by _read_data_file if lazy=True and if Neo has a RawIO
                # that supports the file format
                if hasattr(self.blk, 'rawio') and isinstance(self.blk.rawio, neo.rawio.baserawio.BaseRawIO):
                    io = self.blk.rawio
                    if io.support_lazy:
                        lazy_load_signals = True

            if lazy_load_signals:

                # Intan-specific tricks
                if isinstance(io, neo.io.IntanIO):
                    # dirty trick for getting ungrouped channels into a single source
                    io.header['signal_channels']['group_id'] = 0

                    # prepare to append custom channel names stored in data file to ylabels
                    custom_channel_names = {c['native_channel_name']: c['custom_channel_name'] for c in io._ordered_channels}

                channel_indexes = [p['index'] for p in self.metadata['plots']]
                sources['signal'].append(ephyviewer.AnalogSignalFromNeoRawIOSource(io, channel_indexes))

                # modify loaded channel names to use ylabels
                for i, p in enumerate(self.metadata['plots']):

                    ylabel = p['ylabel']

                    # Intan-specific tricks
                    if isinstance(io, neo.io.IntanIO):
                        # append custom channel names stored in data file to ylabels
                        if custom_channel_names[p['channel']] != ylabel:
                            ylabel += ' ({})'.format(custom_channel_names[p['channel']])

                    sources['signal'][-1].channels['name'][i] = ylabel

                # TODO support scatter from tridesclous_file

            else: # lazy==False or io.support_lazy==False

                # even if lazy==True, signals do not need to be loaded now
                # because load_dataset will have already taken care of that and
                # saved them in blk when it detected that Neo did not support
                # lazy loading for the given file reader

                # prepare scatter plot parameters
                plotNameToIndex = {p['channel']:i for i, p in enumerate(self.metadata['plots'])}
                all_times = sigs[0].times.rescale('s').magnitude # assuming all AnalogSignals have the same sampling rate and start time
                spike_indices = {}
                spike_channels = {}
                for st in seg.spiketrains:
                    if 'channels' in st.annotations:
                        c = []
                        for channel in st.annotations['channels']:
                            index = plotNameToIndex.get(channel, None)
                            if index is None:
                                logger.warning('Spike train {} will not be plotted on channel {} because that channel isn\'t being plotted'.format(st.name, channel))
                            else:
                                c.append(index)
                        if c:
                            spike_channels[st.name] = c
                            spike_indices[st.name] = np.where(np.isin(all_times, st.times.magnitude))[0]

                sources['signal'].append(ephyviewer.AnalogSignalSourceWithScatter(
                    signals = np.concatenate([sigs[p['index']].magnitude for p in self.metadata['plots']], axis = 1),
                    sample_rate = sigs[0].sampling_rate.rescale('Hz'), # assuming all AnalogSignals have the same sampling rate
                    t_start = sigs[0].t_start.rescale('s'),            # assuming all AnalogSignals start at the same time
                    channel_names = [p['ylabel'] for p in self.metadata['plots']],
                    scatter_indexes = spike_indices,
                    scatter_channels = spike_channels,
                ))

                # instead of passing colors into AnalogSignalSourceWithScatter
                # constructor with scatter_colors, first let the constructor
                # choose reasonable default colors (done above), and only then
                # override colors for units that have been explicitly set in
                # amplitude_discriminators (done here)
                sources['signal'][-1].scatter_colors.update(unit_colors)

            # useOpenGL=True eliminates the extremely poor performance associated
            # with TraceViewer's line_width > 1.0, but it also degrades overall
            # performance somewhat and is reportedly unstable
            if support_increased_line_width:
                useOpenGL = True
                line_width = 2.0
            else:
                useOpenGL = None
                line_width = 1.0

            trace_view = ephyviewer.TraceViewer(source = sources['signal'][0], name = 'Signals', useOpenGL = useOpenGL)

            win.add_view(trace_view)

            trace_view.params['xratio'] = self.metadata.get('past_fraction', 0.3)
            trace_view.params['auto_scale_factor'] = 0.02
            trace_view.params['scatter_size'] = ui_scales[ui_scale]['scatter_size']
            trace_view.params['line_width'] = line_width
            trace_view.params['label_size'] = ui_scales[ui_scale]['channel_label_size']
            trace_view.params['display_labels'] = True
            trace_view.params['antialias'] = True

            # set the theme
            if theme != 'original':
                trace_view.params['background_color'] = self.themes[theme]['background_color']
                trace_view.params['vline_color'] = self.themes[theme]['vline_color']
                trace_view.params['label_fill_color'] = self.themes[theme]['label_fill_color']
                trace_view.params_controller.combo_cmap.setCurrentText(self.themes[theme]['cmap'])
                trace_view.params_controller.on_automatic_color()

            # set explicitly assigned signal colors
            for name, color in sig_colors.items():
                try:
                    index = [p['channel'] for p in self.metadata['plots']].index(name)
                    trace_view.by_channel_params['ch{}'.format(index), 'color'] = color
                except ValueError:
                    # sig name may not have been found in the trace list
                    pass

            # adjust plot range, scaling, and positioning
            trace_view.params['ylim_max'] = 0.5
            trace_view.params['ylim_min'] = -trace_view.source.nb_channel + 0.5
            trace_view.params['scale_mode'] = 'by_channel'
            for i, p in enumerate(self.metadata['plots']):
                sig_units = sigs[p['index']].units
                units_ratio = (pq.Quantity(1, p['units'])/pq.Quantity(1, sig_units)).simplified
                assert units_ratio.dimensionality.string == 'dimensionless', f"Channel \"{p['channel']}\" has units {sig_units} and cannot be converted to {p['units']}"
                ylim_span = np.ptp(p['ylim'] * units_ratio.magnitude)
                ylim_center = np.mean(p['ylim'] * units_ratio.magnitude)
                trace_view.by_channel_params['ch{}'.format(i), 'gain'] = 1/ylim_span # rescale [ymin,ymax] across a unit
                trace_view.by_channel_params['ch{}'.format(i), 'offset'] = -i - ylim_center/ylim_span # center [ymin,ymax] within the unit

        ########################################################################
        # TRACES OF RAUC

        if self.is_shown('traces_rauc'):

            rauc_sigs = [sig.annotations['rauc_sig'] for sig in sigs if 'rauc_sig' in sig.annotations]

            if rauc_sigs:

                sig_rauc_source = ephyviewer.InMemoryAnalogSignalSource(
                    signals = np.concatenate([rauc_sigs[p['index']].as_array() for p in self.metadata['plots']], axis = 1),
                    sample_rate = rauc_sigs[0].sampling_rate.rescale('Hz'), # assuming all AnalogSignals have the same sampling rate
                    t_start = rauc_sigs[0].t_start.rescale('s'),            # assuming all AnalogSignals start at the same time
                    channel_names = [p['ylabel'] + ' RAUC' for p in self.metadata['plots']],
                )
                sources['signal_rauc'] = [sig_rauc_source]

                trace_rauc_view = ephyviewer.TraceViewer(source = sources['signal_rauc'][0], name = 'Integrated signals (RAUC)')

                if 'Signals' in win.viewers:
                    win.add_view(trace_rauc_view, tabify_with = 'Signals')
                else:
                    win.add_view(trace_rauc_view)

                trace_rauc_view.params['xratio'] = self.metadata.get('past_fraction', 0.3)
                trace_rauc_view.params['line_width'] = line_width
                trace_rauc_view.params['label_size'] = ui_scales[ui_scale]['channel_label_size']
                trace_rauc_view.params['display_labels'] = True
                trace_rauc_view.params['display_offset'] = True
                trace_rauc_view.params['antialias'] = True

                # set the theme
                if theme != 'original':
                    trace_rauc_view.params['background_color'] = self.themes[theme]['background_color']
                    trace_rauc_view.params['vline_color'] = self.themes[theme]['vline_color']
                    trace_rauc_view.params['label_fill_color'] = self.themes[theme]['label_fill_color']
                    trace_rauc_view.params_controller.combo_cmap.setCurrentText(self.themes[theme]['cmap'])
                    trace_rauc_view.params_controller.on_automatic_color()

                # set explicitly assigned signal colors
                for name, color in sig_colors.items():
                    try:
                        index = [p['channel'] for p in self.metadata['plots']].index(name)
                        trace_rauc_view.by_channel_params['ch{}'.format(index), 'color'] = color
                    except ValueError:
                        # sig name may not have been found in the rauc trace list
                        pass

                # adjust plot range
                trace_rauc_view.params['ylim_max'] = 0.5
                trace_rauc_view.params['ylim_min'] = -trace_rauc_view.source.nb_channel + 0.5
                trace_rauc_view.params['scale_mode'] = 'by_channel'
                for i, p in enumerate(self.metadata['plots']):
                    ylim_span = np.median(rauc_sigs[p['index']].magnitude) * 10
                    ylim_center = ylim_span / 2
                    trace_rauc_view.by_channel_params['ch{}'.format(i), 'gain'] = 1/ylim_span # rescale [ymin,ymax] across a unit
                    trace_rauc_view.by_channel_params['ch{}'.format(i), 'offset'] = -i - ylim_center/ylim_span # center [ymin,ymax] within the unit

        ########################################################################
        # FREQUENCY (EXPERIMENTAL AND COMPUTATIONALLY EXPENSIVE!)

        if self.is_shown('freqs'):

            freq_view = ephyviewer.TimeFreqViewer(source = trace_view.source, name = 'Time-Frequency')

            freq_view.params['xratio'] = self.metadata.get('past_fraction', 0.3)
            freq_view.params['scale_mode'] = 'by_channel'
            freq_view.params['nb_column'] = 1
            freq_view.params['colormap'] = 'gray'
            freq_view.params.param('timefreq')['deltafreq'] = 100
            freq_view.params.param('timefreq')['f_start'] = 1
            freq_view.params.param('timefreq')['f_stop'] = 1500

            freq_view.by_channel_params['ch0', 'visible'] = False
            freq_view.by_channel_params['ch1', 'visible'] = True
            freq_view.by_channel_params['ch2', 'visible'] = True
            freq_view.by_channel_params['ch3', 'visible'] = True
            freq_view.by_channel_params['ch4', 'visible'] = False

            # freq_view.params.param('timefreq')['normalisation'] = 1.5
            freq_view.by_channel_params['ch1', 'clim'] = 3
            freq_view.by_channel_params['ch2', 'clim'] = 5
            freq_view.by_channel_params['ch3', 'clim'] = 10

            if 'Signals' in win.viewers:
                win.add_view(freq_view, tabify_with = 'Signals')
            elif 'Integrated signals (RAUC)' in win.viewers:
                win.add_view(freq_view, tabify_with = 'Integrated signals (RAUC)')
            else:
                win.add_view(freq_view)

        ########################################################################
        # SPIKE TRAINS

        if self.is_shown('spike_trains') and sources['spike'][0].nb_channel > 0:

            spike_train_view = ephyviewer.SpikeTrainViewer(source = sources['spike'][0], name = 'Spike trains')
            win.add_view(spike_train_view)

            # set the theme
            if theme != 'original':
                spike_train_view.params['background_color'] = self.themes[theme]['background_color']
                spike_train_view.params['vline_color'] = self.themes[theme]['vline_color']
                spike_train_view.params['label_fill_color'] = self.themes[theme]['label_fill_color']
                spike_train_view.params_controller.combo_cmap.setCurrentText(self.themes[theme]['cmap'])
                spike_train_view.params_controller.on_automatic_color()

            # set explicitly assigned unit colors
            for name, color in unit_colors.items():
                try:
                    index = [st.name for st in seg.spiketrains].index(name)
                    spike_train_view.by_channel_params['ch{}'.format(index), 'color'] = color
                except ValueError:
                    # unit name may not have been found in the spike train list
                    pass

            spike_train_view.params['xratio'] = self.metadata.get('past_fraction', 0.3)
            spike_train_view.params['label_size'] = ui_scales[ui_scale]['channel_label_size']

        ########################################################################
        # TRACES OF FIRING RATES

        if self.is_shown('traces_rates'):

            firing_rate_sigs = [st.annotations['firing_rate_sig'] for st in seg.spiketrains if 'firing_rate_sig' in st.annotations]

            if firing_rate_sigs:

                sig_rates_source = ephyviewer.InMemoryAnalogSignalSource(
                    signals = np.concatenate([sig.as_array() for sig in firing_rate_sigs], axis = 1),
                    sample_rate = firing_rate_sigs[0].sampling_rate.rescale('Hz'), # assuming all AnalogSignals have the same sampling rate
                    t_start = firing_rate_sigs[0].t_start.rescale('s'),            # assuming all AnalogSignals start at the same time
                    channel_names = [sig.name for sig in firing_rate_sigs],
                )
                sources['signal_rates'] = [sig_rates_source]

                trace_rates_view = ephyviewer.TraceViewer(source = sources['signal_rates'][0], name = 'Firing rates')

                if 'Spike trains' in win.viewers:
                    win.add_view(trace_rates_view, tabify_with = 'Spike trains')
                else:
                    win.add_view(trace_rates_view)

                trace_rates_view.params['xratio'] = self.metadata.get('past_fraction', 0.3)
                trace_rates_view.params['line_width'] = line_width
                trace_rates_view.params['label_size'] = ui_scales[ui_scale]['channel_label_size']
                trace_rates_view.params['display_labels'] = True
                trace_rates_view.params['display_offset'] = True
                trace_rates_view.params['antialias'] = True

                # set the theme
                if theme != 'original':
                    trace_rates_view.params['background_color'] = self.themes[theme]['background_color']
                    trace_rates_view.params['vline_color'] = self.themes[theme]['vline_color']
                    trace_rates_view.params['label_fill_color'] = self.themes[theme]['label_fill_color']
                    trace_rates_view.params_controller.combo_cmap.setCurrentText(self.themes[theme]['cmap'])
                    trace_rates_view.params_controller.on_automatic_color()

                # set explicitly assigned firing rate sig colors
                for name, color in unit_colors.items():
                    try:
                        index = [sig.name for sig in firing_rate_sigs].index(name)
                        trace_rates_view.by_channel_params['ch{}'.format(index), 'color'] = color
                    except ValueError:
                        # unit name may not have been found in the firing rate sig list
                        pass

                # adjust plot range
                trace_rates_view.params['ylim_max'] = 0.5
                trace_rates_view.params['ylim_min'] = -trace_rates_view.source.nb_channel + 0.5
                trace_rates_view.params['scale_mode'] = 'by_channel'
                for i, sig in enumerate(firing_rate_sigs):
                    ylim_span = 10
                    ylim_center = ylim_span / 2
                    trace_rates_view.by_channel_params['ch{}'.format(i), 'gain'] = 1/ylim_span # rescale [ymin,ymax] across a unit
                    trace_rates_view.by_channel_params['ch{}'.format(i), 'offset'] = -i - ylim_center/ylim_span # center [ymin,ymax] within the unit

        ########################################################################
        # EPOCHS

        if self.is_shown('epochs') and sources['epoch'][0].nb_channel > 0:

            epoch_view = ephyviewer.EpochViewer(source = sources['epoch'][0], name = 'Epochs')
            win.add_view(epoch_view)

            # set the theme
            if theme != 'original':
                epoch_view.params['background_color'] = self.themes[theme]['background_color']
                epoch_view.params['vline_color'] = self.themes[theme]['vline_color']
                epoch_view.params['label_fill_color'] = self.themes[theme]['label_fill_color']
                epoch_view.params_controller.combo_cmap.setCurrentText(self.themes[theme]['cmap'])
                epoch_view.params_controller.on_automatic_color()

            # set explicitly assigned unit colors
            for name, color in unit_colors.items():
                try:
                    index = [ep['name'] for ep in sources['epoch'][0].all].index(name + ' burst')
                    epoch_view.by_channel_params['ch{}'.format(index), 'color'] = color
                except ValueError:
                    # unit burst name may not have been found in the epoch list
                    pass

            epoch_view.params['xratio'] = self.metadata.get('past_fraction', 0.3)
            epoch_view.params['label_size'] = ui_scales[ui_scale]['channel_label_size']

        ########################################################################
        # EPOCH ENCODER

        if self.is_shown('epoch_encoder') and self.metadata.get('epoch_encoder_file', None) is not None:

            possible_labels = self.metadata.get('epoch_encoder_possible_labels', [])

            # append labels found in the epoch encoder file but not in the
            # epoch_encoder_possible_labels list, preserving the original
            # ordering of epoch_encoder_possible_labels
            labels_from_file = [ep.name for ep in seg.epochs if len(ep.times) > 0 and '(from epoch encoder file)' in ep.labels]
            for label in labels_from_file:
                if label not in possible_labels:
                    possible_labels.append(label)

            if not possible_labels:

                # an empty epoch encoder file and an empty list of possible
                # labels were provided
                logger.warning('Ignoring epoch_encoder_file because epoch_encoder_possible_labels was unspecified')

            else:

                writable_epoch_source = NeuroticWritableEpochSource(
                    filename = _abs_path(self.metadata, 'epoch_encoder_file'),
                    possible_labels = possible_labels,
                )

                epoch_encoder = ephyviewer.EpochEncoder(source = writable_epoch_source, name = 'Epoch encoder')
                epoch_encoder.params['exclusive_mode'] = False
                win.add_view(epoch_encoder)

                # set the theme
                if theme != 'original':
                    epoch_encoder.params['background_color'] = self.themes[theme]['background_color']
                    epoch_encoder.params['vline_color'] = self.themes[theme]['vline_color']
                    epoch_encoder.params['label_fill_color'] = self.themes[theme]['label_fill_color']
                    # TODO add support for combo_cmap

                epoch_encoder.params['xratio'] = self.metadata.get('past_fraction', 0.3)
                epoch_encoder.params['label_size'] = ui_scales[ui_scale]['channel_label_size']

        ########################################################################
        # VIDEO

        if self.is_shown('video') and self.metadata.get('video_file', None) is not None:

            video_source = ephyviewer.MultiVideoFileSource(video_filenames = [_abs_path(self.metadata, 'video_file')])

            # some video files are loaded with an incorrect start time, so
            # reset video start to zero
            video_source.t_stops[0] -= video_source.t_starts[0]
            video_source.t_starts[0] = 0

            # apply the video_offset
            if self.metadata.get('video_offset', None) is not None:
                video_source.t_starts[0] += self.metadata['video_offset']
                video_source.t_stops[0]  += self.metadata['video_offset']

            # correct for videos that report frame rates that are too fast or
            # too slow compared to the clock on the data acquisition system
            if self.metadata.get('video_rate_correction', None) is not None:
                video_source.rates[0] *= self.metadata['video_rate_correction']

            if self.metadata.get('video_jumps', None) is not None:

                # create an unmodified video_times vector with evenly spaced times
                video_times = np.arange(video_source.nb_frames[0])/video_source.rates[0] + video_source.t_starts[0]

                # insert repeating times at pause_start to fill pause_duration
                # so that that section of the video is skipped over
                for pause_start, pause_duration in self.metadata['video_jumps']:
                    pause_start_index = np.searchsorted(video_times, pause_start)
                    pause_fill = video_times[pause_start_index] * np.ones(int(np.round(pause_duration*video_source.rates[0])))
                    video_times = np.insert(video_times, pause_start_index, pause_fill)
                    video_times = video_times[:video_source.nb_frames[0]]

                # add the modified video_times to the video_source
                video_source.video_times = [video_times]
                video_source.t_starts[0] = min(video_times)
                video_source.t_stops[0]  = max(video_times)

            # update the source-level times from the modified file-level times
            video_source._t_start = max(min(video_source.t_starts), 0)
            video_source._t_stop  = max(video_source.t_stops)

            video_view = ephyviewer.VideoViewer(source = video_source, name = 'Video')
            if theme != 'original':
                video_view.graphiclayout.setBackground(self.themes[theme]['background_color'])
            win.add_view(video_view, location = 'bottom', orientation = 'horizontal')

        ########################################################################
        # EVENTS

        if self.is_shown('event_list') and sources['event'][0].nb_channel > 0:

            event_list = ephyviewer.EventList(source = sources['event'][0], name = 'Events')
            if 'Video' in win.viewers:
                win.add_view(event_list, split_with = 'Video')
            else:
                win.add_view(event_list, location = 'bottom', orientation = 'horizontal')

        ########################################################################
        # DATAFRAME

        annotations_dataframe = _neo_epoch_to_dataframe(seg.epochs, exclude_epoch_encoder_epochs=True)
        if self.is_shown('data_frame') and len(annotations_dataframe) > 0:

            data_frame_view = ephyviewer.DataFrameView(source = annotations_dataframe, name = 'Table')
            if 'Events' in win.viewers:
                win.add_view(data_frame_view, tabify_with = 'Events')
            elif 'Video' in win.viewers:
                win.add_view(data_frame_view, split_with = 'Video')
            else:
                win.add_view(data_frame_view, location = 'bottom', orientation = 'horizontal')

        ########################################################################
        # FINAL TOUCHES

        # select first tabs
        for widget in win.children():
            if isinstance(widget, ephyviewer.PyQt5.QtWidgets.QTabBar):
                widget.setCurrentIndex(0)

        # set amount of time shown initially
        win.set_xsize(self.metadata.get('t_width', 40)) # seconds

        return win

def _set_defaults_for_plots(metadata, blk):
    """
    Set defaults for plot channels, units, ylim, and ylabel if these
    parameters are missing from ``metadata``.
    """

    sigs = blk.segments[0].analogsignals
    signalNameToIndex = {sig.name:i for i, sig in enumerate(sigs)}

    if metadata.get('plots', None) is None:
        metadata['plots'] = [{'channel': sig.name} for sig in sigs if _default_keep_signal(sig)]

    plots = []
    for plot in metadata['plots']:
        index = signalNameToIndex.get(plot['channel'], None)
        if index is None:
            logger.warning('Removing plot with channel name "{}" because channel was not found in blk!'.format(plot['channel']))
        else:
            plot['index'] = index
            plot.setdefault('units',  _default_units(sigs[index]))
            plot.setdefault('ylim',   _default_ylim(sigs[index]))
            plot.setdefault('ylabel', sigs[index].name)
            plots.append(plot)
    metadata['plots'] = plots

    return metadata['plots']

def _default_keep_signal(sig):
    """
    If ``plots`` is not specified in ``metadata``, this function determines
    which channels are plotted by default.
    """
    return (not sig.name.startswith('Analog Input #')) and (sig.name != 'Clock')

def _default_units(sig):
    """
    If ``plots`` is missing ``units`` in ``metadata``, this function determines
    default units.
    """

    mapping = {
        'V': 'uV', # convert voltages to microvolts
        'N': 'mN', # convert forces to millinewtons
    }
    mapping = {pq.Quantity(1, k).dimensionality.simplified: v for k, v in mapping.items()}
    return mapping.get(sig.units.dimensionality.simplified, sig.units)

def _default_ylim(sig):
    """
    If ``plots`` is missing ``ylim`` in ``metadata``, this function determines
    default plot ranges.
    """

    mapping = {
        'V': [-120, 120], # plot range for voltages
        'N': [ -10, 300], # plot range for forces
    }
    mapping = {pq.Quantity(1, k).dimensionality.simplified: v for k, v in mapping.items()}
    return mapping.get(sig.units.dimensionality.simplified, [-1, 1])

def _neo_epoch_to_dataframe(neo_epochs, exclude_epoch_encoder_epochs=False):
    """
    Convert a list of Neo Epochs into a dataframe.
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
        if len(ep.times) > 0 and (not exclude_epoch_encoder_epochs or '(from epoch encoder file)' not in ep.labels):
            data = np.array([ep.times, ep.times+ep.durations, ep.durations, [ep.name]*len(ep), ep.labels]).T
            df = pd.concat([df, pd.DataFrame(data, columns=columns)], ignore_index=True)
    return df.astype(dtype=dtypes).sort_values(['Start (s)', 'End (s)', 'Type', 'Label']).reset_index(drop=True)

def _estimate_video_jump_times(blk):
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
        note_start_times = np.array([0], dtype=int)
        note_stop_times = np.array([], dtype=int)
        for note_line in blk.annotations['notes'].split('\n'):
            m = re.match(r'\d\d\d: Start at (\d*) s', note_line)
            if m:
                note_start_times = np.append(note_start_times, int(m.group(1)))
            m = re.match(r'\d\d\d: Stop at (\d*) s', note_line)
            if m:
                note_stop_times = np.append(note_stop_times, int(m.group(1)))

        # calculate approximate pause durations
        pause_durations = note_start_times[1:]-note_stop_times[:-1]

        # obtain exact stop times (AxoGraph time, not video time)
        event_stop_times = np.array([], dtype=float)
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
