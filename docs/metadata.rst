.. _config-metadata:

Configuring Metadata
====================

To load your data with *neurotic*, you must organize them in one or more YAML
files, called *metadata files*.

YAML files are very sensitive to punctuation and indentation, so mind those
details carefully! Importantly, the tab character cannot be used for
indentation; use spaces instead. There are `many free websites
<https://www.google.com/search?q=yaml+validator>`__ that can validate YAML for
you.

You may include comments in your metadata file, which should begin with ``#``.

.. _config-metadata-top-level:

Top-Level Organization
----------------------

Datasets listed within the same metadata file must be given unique names, which
may include spaces. The special name ``neurotic_config`` is reserved for
*neurotic* configuration settings and cannot be used for datasets.

In addition to names, a long description can be provided for each dataset.

Details pertaining to each dataset, including the description, are nested
beneath the dataset name using indentation. You may need to use double quotes
around names, descriptions, or other text if they contain special characters
(such as ``:`` or ``#``) or are composed only of numbers (such as a date).

.. code-block:: yaml

    experiment 2020-01-01:
        description: Both the name and description will be visible when neurotic loads the metadata
        # other details about this dataset will go here

    my favorite dataset:
        description: This time it actually worked!
        # other details about this dataset will go here

.. _config-metadata-local-data:

Specifying Data Locations
-------------------------

Within a dataset's YAML block, paths to data and video files should be
provided.

All files associated with a dataset should be collected into a single
directory. A path to the local copy of this directory can be provided using the
``data_dir`` key. You may specify ``data_dir`` as an absolute path (e.g.,
``C:\Users\me\folder``) or as a path relative to the metadata file (e.g.,
``folder``). If left unspecified, the directory containing the metadata file is
used.

Paths to individual files within the dataset are provided using keys listed
below. These paths should be given relative to ``data_dir``. If ``data_dir`` is
flat (no subdirectories), these should be simply the file names.

======================  ========================================================
Key                     Description
======================  ========================================================
``data_file``           A single Neo_-compatible data file (see :mod:`neo.io`
                        for file formats)
``video_file``          A video file that can be synchronized with ``data_file``
``annotations_file``    A CSV file for read-only annotations
``epoch_encoder_file``  A CSV file for annotations writable by the epoch encoder
``tridesclous_file``    A CSV file output by tridesclous_'s :meth:`DataIO.export_spikes <tridesclous.dataio.DataIO.export_spikes>`
======================  ========================================================

Note that the ``annotations_file`` must contain exactly 4 columns with
these headers: "Start (s)", "End (s)", "Type", and "Label".

The ``epoch_encoder_file`` must contain exactly 3 columns with these headers:
"Start (s)", "End (s)", and "Type". (The fourth column is missing because
ephyviewer's epoch encoder is currently unable to attach notes to individual
epochs; this may be improved upon in the future.)

The ``tridesclous_file`` is described in more detail in
:ref:`config-metadata-tridesclous`.

.. _config-metadata-remote-data:

Remote Data Available for Download
----------------------------------

Data files must be stored on the local computer for *neurotic* to load them and
display their contents. If the files are available for download from a remote
server (e.g., a web site, an FTP server, or Google Drive), *neurotic* can be
configured to download them for you to the local directory specified by
``data_dir`` if the files aren't there already.

Specify the URL to the directory containing the data on the remote server using
``remote_data_dir``. *neurotic* expects the local ``data_dir`` and the
``remote_data_dir`` to have the same structure and will mirror the
``remote_data_dir`` in the local ``data_dir`` when you download data (not a
complete mirror, just the specified files).

For an example, consider the following:

.. code-block:: yaml

    my favorite dataset:
        data_dir:           C:\Users\me\folder
        remote_data_dir:    http://myserver/remote_folder
        data_file:          data.axgx
        video_file:         video.mp4

With a metadata file like this, the file paths ``data_file`` and ``video_file``
are appended to ``remote_data_dir`` to obtain the complete URLs for downloading
these files, and they will be saved to the local ``data_dir``.

If you have many datasets hosted by the same server, you can specify the server
URL just once using the special ``remote_data_root`` key, which should be
nested under the reserved name ``neurotic_config`` outside of any dataset's
YAML block. This allows you to provide for each dataset a partial URL to a
folder in ``remote_data_dir`` which is relative to ``remote_data_root``. For
example:

.. code-block:: yaml

    neurotic_config:  # reserved name for global settings
        remote_data_root:   http://myserver

    my favorite dataset:
        data_dir:           C:\Users\me\folder1
        remote_data_dir:    remote_folder1
        data_file:          data.axgx
        video_file:         video.mp4

    another dataset:
        data_dir:           C:\Users\me\folder2
        remote_data_dir:    remote_folder2
        data_file:          data.axgx
        video_file:         video.mp4

Here, URLs to video files are composed by joining ``remote_data_root`` +
``remote_data_dir`` + ``video_file``.

Recall that if ``data_dir`` is a relative path, it is assumed to be relative
to the metadata file. In the example above, if the metadata file is located in
``C:\Users\me``, the paths could be abbreviated:

.. code-block:: yaml

    neurotic_config:
        remote_data_root:   http://myserver

    my favorite dataset:
        data_dir:           folder1
        remote_data_dir:    remote_folder1
        data_file:          data.axgx
        video_file:         video.mp4

    another dataset:
        data_dir:           folder2
        remote_data_dir:    remote_folder2
        data_file:          data.axgx
        video_file:         video.mp4

.. _portability:

.. note::

    **Portability is easy with neurotic!** Use relative paths in your metadata
    file along with a remotely accessible data store such as GIN_ or a Shared
    Drive on Google Drive (see details below) to make your metadata file fully
    portable. The example above is a simple model of this style. A metadata
    file like this can be copied to a different computer, and downloaded files
    will automatically be saved to the right place. Data stores can be password
    protected and *neurotic* will prompt you for a user name and password. This
    makes it easy to share the *neurotic* experience with your colleagues! 🤪

.. _gdrive-urls:

URLs to Use with Google Drive
.............................

After completing some essential manual setup (see :ref:`gdrive`), *neurotic*
can retrieve remote files from Google Drive using URL-like paths of the
following form::

    gdrive://<drive name>/<folder 1>/<...>/<folder N>/<file name>

The ``<drive name>`` may be "``My Drive``" for files located in a personal
Google Drive, or it may be the name of a Shared Drive that the user has
permission to access.

Note that these URL-like paths are not equivalent to ordinary URLs
associated with Google Drive files, such as shareable links, which are
composed of pseudorandom file IDs and do not reveal anything about the name
of the file or the folders containing it. Instead, these URL-like paths allow
you to structure your metadata with the file tree hierarchy in mind, so that
relative paths can be used.

For example, with datasets stored in subdirectories "datasets/A", "datasets/B",
etc., of a Shared Drive titled "Lab Project Data", you
could use this metadata to mirror the files locally:

.. code-block:: yaml

    neurotic_config:
        remote_data_root:   gdrive://Lab Project Data/datasets

    Dataset A:
        data_dir:           A
        remote_data_dir:    A
        data_file:          data.axgx
        video_file:         video.mp4

    Dataset B:
        data_dir:           B
        remote_data_dir:    B
        data_file:          data.axgx
        video_file:         video.mp4

.. _gin-urls:

URLs to Use with GIN
....................

If you have data stored in a **public** repository on GIN_, you can access it
from a URL of this form::

    https://gin.g-node.org/<username>/<reponame>/raw/master/<path>

For **private** repositories, you must use a different URL that takes advantage
of the WebDAV protocol::

    https://gin.g-node.org/<username>/<reponame>/_dav/<path>

The second form works with public repos too, but GIN login credentials are
still required. Consequently, the first form is more convenient for public
repos.

.. _congig-metadata-globals:

Global Configuration Settings
-----------------------------

The top-level name ``neurotic_config`` is reserved for configuration settings
that apply to all datasets or to the app itself. The following settings may be
nested beneath ``neurotic_config``.

======================  ========================================================
Key                     Description
======================  ========================================================
``neurotic_version``    A `version specification`_ stating the version of
                        *neurotic* required by the metadata. Presently, if the
                        requirement is not met, only a warning is issued.
                        Quotation marks around the spec are usually required.
``remote_data_root``    A URL prepended to each ``remote_data_dir`` that is not
                        already a full URL (i.e., does not already begin with a
                        protocol scheme like ``https://``)
======================  ========================================================

For example:

.. code-block:: yaml

    neurotic_config:
        neurotic_version:   '>=1.4,<2'
        remote_data_root:   http://myserver

    my favorite dataset:
        # dataset details here

.. _config-metadata-neo-io:

Data Reader (Neo) Settings
--------------------------

The electrophysiology file specified by ``data_file`` is read using Neo_, which
supports many file types. A complete list of the implemented formats can be
found here: :mod:`neo.io`.

By default, *neurotic* will use the file extension of ``data_file`` to guess
the file format and choose the appropriate Neo IO class for reading it. If the
guess fails, you can force *neurotic* to use a different class by specifying
the class name with the ``io_class`` parameter (all available classes are
listed here: :mod:`neo.io`).

Some Neo IO classes accept additional arguments beyond just a filename (see the
Neo docs for details: :mod:`neo.io`). You can specify these arguments in your
metadata using the ``io_args`` parameter.

For example, suppose you have data stored in a plain text file that is missing
a file extension. The :class:`neo.io.AsciiSignalIO` class can read plain text
files, but you must specify this manually using ``io_class`` because the
extension is missing. You could do this and pass in supported arguments in the
following way:

.. code-block:: yaml

    my favorite dataset:
        data_file: plain_text_file_without_file_extension

        io_class: AsciiSignalIO

        io_args:
            skiprows: 1 # skip header
            delimiter: ' ' # space-delimited
            t_start: 5 # sec
            sampling_rate: 1000 # Hz
            units: mV

.. _config-metadata-video:

Video Synchronization Parameters
--------------------------------

.. _config-metadata-video-offset:

Constant Offset
...............

If data acquisition began with some delay after video capture began, provide a
negative value for ``video_offset`` equal to the delay in seconds. If video
capture began after the start of data acquisition, use a positive value. A
value of zero will have no effect.

*neurotic* warns users about the risk of async if ``video_file`` is given but
``video_offset`` is not. To eliminate this warning for videos that have no
delay, provide zero.

.. _config-metadata-video-rate:

Frame Rate Correction
.....................

If the average frame rate reported by the video file is a little fast or slow,
you may notice your video and data going out of sync late in a long experiment.
You can provide the ``video_rate_correction`` parameter to fix this. The
reported average frame rate of the video file will be multiplied by this factor
to obtain a new frame rate used for playback. A value less than 1 will decrease
the frame rate and shift video events to later times. A value greater than 1
will increase the frame rate and shift video events to earlier times. A value
of 1 has no effect.

You can obtain a good estimate of what value to use by taking the amount of
time between two events in the video and dividing by the amount of time between
the same two events according to the data record (seen, for example, as
synchronization pulses or as movement artifacts).

.. _config-metadata-video-jumps:

Discrete Desynchronization Events
.................................

If you paused data acquisition during your experiment while video capture was
continuous, you can use the ``video_jumps`` parameter to correct for these
discrete desynchronization events, assuming you have some means of
reconstructing the timing. For each pause, provide an ordered pair of numbers
in seconds: The first is the time *according to data acquisition* (not
according to the video) when the pause occurred, and the second is the duration
of the pause during which the video kept rolling.

For example:

.. code-block:: yaml

    my favorite dataset:
        video_file: video.mp4
        # etc

        video_jumps:
            # a list of ordered pairs containing:
            # (1) time in seconds when paused occurred according to DAQ
            # (2) duration of pause in seconds
            - [60, 10]
            - [120, 10]
            - [240, 10]

These values could correct for three 10-second pauses occurring at times 1:00,
2:00, 3:00 according to the DAQ, which would correspond to times 1:00, 2:10,
3:20 according to the video. The extra video frames captured during the pauses
will be excised from playback so that the data and video remain synced.

*neurotic* will automatically suggest values for ``video_jumps`` if it reads an
AxoGraph file that contains stops and restarts (only if ``video_jumps`` is not
already specified).

.. _config-metadata-datetime:

Real-World Date and Time
------------------------

The GUI can optionally display the real-world date and time. This feature is
accurate only if the recording is continuous (no interruptions or pauses during
recording) and the start time of the recording is known. Some data file formats
may store the start time of the recording, in which case *neurotic* will use
that information automatically. However, if the start time is missing or
inaccurate, it can be specified in the metadata like this:

.. code-block:: yaml

    my favorite dataset:
        data_file: data.axgx
        rec_datetime: 2020-01-01 13:14:15
        # etc

.. _config-metadata-plots:

Plot Parameters
---------------

Use the ``plots`` parameter to specify which signal channels from ``data_file``
you want plotted and how to scale them. Optionally, a color may be specified
for channels using a single letter color code (e.g., ``'b'`` for blue or
``'k'`` for black) or a hexadecimal color code (e.g., ``'1b9e77'``).

Consider the following example, and notice the use of hyphens and indentation
for each channel.

.. code-block:: yaml

    my favorite dataset:
        data_file: data.axgx
        # etc

        plots:
            - channel: Extracellular
              ylabel: Buccal nerve 2 (BN2)
              units: uV
              ylim: [-150, 150]
              color: r

            - channel: Intracellular
              ylabel: B3 neuron
              units: mV
              ylim: [-100, 50]
              color: '666666'

            - channel: Force
              units: mN
              ylim: [-10, 500]

This would plot the "Extracellular", "Intracellular", and "Force" channels from
the ``data_file`` in the given order. ``ylabel`` is used to relabel a channel
and is optional. The ``units`` and ``ylim`` parameters are used together to
scale each signal such that the given range fits neatly between the traces
above and below it. If ``units`` is not given, they are assumed to be
microvolts for voltage signals and millinewtons for force signals. If ``ylim``
is not given, they default to ``[-120, 120]`` for voltages and ``[-10, 300]``
for forces.

If ``plots`` is not provided, all channels are plotted using the default
ranges, except for channels that match these patterns: "Analog Input #*" and
"Clock". Channels with these names can be plotted if given explicitly by
``plots``.

.. _config-metadata-time-range:

Time Range
----------

The amount of time initially visible can be specified in seconds with
``t_width``.

The position of the vertical line, which represents the current time in each
plot, can be specified as a fraction of the plot range with ``past_fraction``.
A value of 0 places the vertical line at the left edge of each plot;
consequently, everything plotted is "in the future", occurring after the
current time. A value of 1 places the vertical line at the right edge of each
plot; consequently, everything plotted is "in the past", coming before the
current time. The default value of 0.3 causes the first 30% of the plot range
to display "the past" and the last 70% to display "the future".

.. _config-metadata-epoch-encoder:

Epoch Encoder Parameters
------------------------

The labels available to the epoch encoder must be specified ahead of time using
``epoch_encoder_possible_labels`` (this is a current limitation of ephyviewer
that may eventually be improved upon).

For example:

.. code-block:: yaml

    my favorite dataset:
        epoch_encoder_file: epoch-encoder.csv
        # etc

        epoch_encoder_possible_labels:
            - label1
            - label2
            - label3

.. _config-metadata-filters:

Filters
-------

Highpass, lowpass, and bandpass filtering can be applied to signals using the
``filters`` parameter. Note that filters are only applied if fast loading is
off (``lazy=False``).

Consider the following example, and notice the use of hyphens and indentation
for each filter.

.. code-block:: yaml

    my favorite dataset:
        data_file: data.axgx
        # etc

        filters:  # used only if fast loading is off (lazy=False)

            - channel: Extracellular
              highpass: 300 # Hz
              lowpass: 500 # Hz

            - channel: Intracellular
              highpass: 300 # Hz

            - channel: Force
              lowpass: 50 # Hz

Filter cutoffs are given in hertz. Combining ``highpass`` and ``lowpass``
provides bandpass filtering.

.. _config-metadata-amplitude-discriminators:

Amplitude Discriminators
------------------------

Spikes with peaks (or troughs) that fall within amplitude windows given by
``amplitude_discriminators`` can be automatically detected by *neurotic* on the
basis of amplitude. Note that amplitude discriminators are only applied if fast
loading is off (``lazy=False``).

Detected spikes are indicated on the signals with markers, and spike trains are
displayed in a raster plot. Optionally, a color may be specified for an
amplitude discriminator using a single letter color code (e.g., ``'b'`` for
blue or ``'k'`` for black) or a hexadecimal color code (e.g., ``'1b9e77'``).

The algorithm can detect either peaks or troughs in the signal. When both the
lower and upper bounds for amplitude windows are positive, the default behavior
is to detect peaks. When both are negative, the default is to detect troughs.
These defaults can be overridden using ``type: trough`` or ``type: peak``,
respectively. This is useful when, for example, detecting subthreshold
excitatory postsynaptic potentials. If the signs of the bounds differ, explicit
specification of the type is required.

In addition to restricting spike detection for a given unit to an amplitude
window, detection can also be limited in time to overlap with epochs with a
given label.

Consider the following example, and notice the use of hyphens and indentation
for each amplitude discriminator.

.. code-block:: yaml

    my favorite dataset:
        data_file: data.axgx
        # etc

        amplitude_discriminators:  # used only if fast loading is off (lazy=False)

            - name: Unit 1
              channel: Extracellular
              units: uV
              amplitude: [50, 150]
              color: r

            - name: Unit 2
              channel: Extracellular
              units: uV
              amplitude: [20, 50]
              epoch: Unit 2 activity
              color: 'e6ab02'

            - name: Unit 3
              channel: Intracellular
              units: mV
              amplitude: [-10, 60]
              type: peak

Here two units are detected on the "Extracellular" channel with different
amplitude windows, and a third unit is detected on the "Intracellular" channel.
On the "Extracellular" channel, any peaks between 50 and 150 microvolts will be
tagged as a spike belonging to "Unit 1". The discriminator for "Unit 2" detects
smaller peaks, between 20 and 50 microvolts, and it provides the optional
``epoch`` parameter. This restricts detection of "Unit 2" to spikes within the
amplitude window that occur at the same time as epochs labeled "Unit 2
activity". These epochs can be created by the epoch encoder (reload required to
rerun spike detection at launch-time), specified in the read-only
``annotations_file``, or even be contained in the ``data_file`` if the format
supports epochs. Finally, peaks between -10 and +60 millivolts will be detected
on the "Intracellular" channel; because the signs of these bounds differ, the
type (peak or trough) must be explicitly given.

.. _config-metadata-tridesclous:

tridesclous Spike Sorting Results
---------------------------------

tridesclous_ is a sophisticated spike sorting toolkit. The results of a sorting
process can be exported to a CSV file using tridesclous's
:meth:`DataIO.export_spikes <tridesclous.dataio.DataIO.export_spikes>`
function. This file contains two columns: the first is the sample index of a
spike, and the second is the ID for a cluster of spikes. If this file is
specified with ``tridesclous_file``, then a mapping from the cluster IDs to
channels must be provided with ``tridesclous_channels``.

In the following example, notice the lack of hyphens:

.. code-block:: yaml

    my favorite dataset:
        data_file: data.axgx
        tridesclous_file: spikes.csv
        # etc

        tridesclous_channels:
            0: [Channel A, Channel B]
            1: [Channel A]
            2: [Channel B]
            3: [Channel B]
            # etc

Here numeric cluster IDs are paired with a list of channels found in
``data_file`` on which the spikes were detected.

To show only a subset of clusters or to merge clusters, add the
``tridesclous_merge`` parameter.

In this example, note again the punctuation:

.. code-block:: yaml

    my favorite dataset:
        data_file: data.axgx
        tridesclous_file: spikes.csv
        # etc

        tridesclous_channels:
            0: [Channel A, Channel B]
            1: [Channel A]
            2: [Channel B]
            3: [Channel B]
            # etc

        tridesclous_merge:
            - [0, 1]
            - [3]

Now clusters 0 and 1 are combined into a single unit, and only that unit and
cluster 3 are plotted; cluster 2 has been discarded.

.. _config-metadata-firing-rates:

Firing Rates
------------

If spike trains were generated using
:ref:`config-metadata-amplitude-discriminators`, imported from
:ref:`config-metadata-tridesclous`, or included in the ``data_file``, their
smoothed firing rates can be computed. Note that firing rates are computed only
if fast loading is off (``lazy=False``).

Firing rates are plotted as continuous signals. Colors are inherited from
``amplitude_discriminators``, if they are provided there.

Firing rates are computed using a kernel that is convolved with the spike
train. The metadata is specified like this:

.. code-block:: yaml

    my favorite dataset:
        data_file: data.axgx
        # etc

        amplitude_discriminators:  # used only if fast loading is off (lazy=False)

            - name: Unit 1
              channel: Extracellular
              units: uV
              amplitude: [50, 150]

        firing_rates:  # used only if fast loading is off (lazy=False)

            - name: Unit 1
              kernel: GaussianKernel
              sigma: 1.5 # sec

The elephant_ package's :func:`instantaneous_rate
<elephant.statistics.instantaneous_rate>` function is used for calculating
firing rates. See :mod:`elephant.kernels` for the names of kernel classes that
may be used with the ``kernel`` parameter. *neurotic* provides an additional
kernel, :class:`CausalAlphaKernel
<neurotic._elephant_tools.CausalAlphaKernel>`, which may also be used. The
``sigma`` parameter is passed as an argument to the kernel class and should be
given in seconds.

The rate calculation function and kernel classes are sourced from
:mod:`neurotic._elephant_tools`, rather than the elephant_ package itself, to
avoid requiring elephant_ as a package dependency.

.. _config-metadata-burst-detectors:

Firing Frequency Burst Detectors
--------------------------------

If spike trains were generated using
:ref:`config-metadata-amplitude-discriminators`, imported from
:ref:`config-metadata-tridesclous`, or included in the ``data_file``, a simple
burst detection algorithm that relies on instantaneous firing rate thresholds
can be run to detect periods of intense activity. Note that burst detectors are
only applied if fast loading is off (``lazy=False``).

Detected bursts are plotted as epochs. Colors are inherited from
``amplitude_discriminators``, if they are provided there.

Burst detectors are specified in metadata like this:

.. code-block:: yaml

    my favorite dataset:
        data_file: data.axgx
        # etc

        amplitude_discriminators:  # used only if fast loading is off (lazy=False)

            - name: Unit 1
              channel: Extracellular
              units: uV
              amplitude: [50, 150]

        burst_detectors:  # used only if fast loading is off (lazy=False)

            - spiketrain: Unit 1
              name: Unit 1 burst  # optional, used for customizing output epoch name
              thresholds: [10, 8] # Hz

The algorithm works by scanning through the spike train with a name matching
``spiketrain`` (in this example, the spike train generated by the "Unit 1"
amplitude discriminator). When the instantaneous firing frequency (IFF; note
this is *NOT* the same as the :ref:`smoothed firing rate
<config-metadata-firing-rates>`, but rather the inverse of the inter-spike
interval) exceeds the first threshold given (e.g., 10 Hz), a burst of activity
is determined to start. After this, at the first moment when the IFF drops
below the second threshold (e.g., 8 Hz), the burst is determined to end. After
scanning through the entire spike train, many bursts that meet these criteria
may be identified.

Note that in general the end threshold should not exceed the start threshold;
this would essentially be the same as setting the start and end thresholds both
to the greater value.

.. _config-metadata-rauc:

Rectified Area Under the Curve (RAUC)
-------------------------------------

One way to simplify a high-frequency signal is by plotted a time series of the
rectified area under the curve (RAUC). Note that RAUCs are calculated only if
fast loading is off (``lazy=False``).

For each signal, the baseline (mean or median) is optionally subtracted off.
The signal is then rectified (absolute value) and divided into non-overlapping
bins of fixed duration. Finally, the integral is calculated within each bin.
The result is a new time series that represents the overall activity of the
original signal. RAUC time series are plotted separately from the original
signals in a second tab. Colors are inherited from ``plots``, if they are
provided there.

The choice of baseline is controlled by the ``rauc_baseline`` metadata
parameter, which may have the value ``None`` (default), ``'mean'``, or
``'median'``. The size of the bins determines how smooth the RAUC time series
is and is set by ``rauc_bin_duration``, given in seconds. If
``rauc_bin_duration`` is not specified (default ``None``), RAUC time series
will not be calculated.


.. _elephant:               https://elephant.readthedocs.io/en/latest
.. _GIN:                    https://gin.g-node.org
.. _Neo:                    https://github.com/NeuralEnsemble/python-neo
.. _tridesclous:            https://github.com/tridesclous/tridesclous
.. _version specification:  https://www.python.org/dev/peps/pep-0440/#version-specifiers
