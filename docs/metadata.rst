.. _config-metadata:

Configuring Metadata
====================

To load your data with **neurotic**, you must organized them in one or more
YAML files, called *metadata files*.

YAML files are very sensitive to punctuation and indentation, so mind those
details carefully! Importantly, the tab character cannot be used for
indentation; use spaces instead. There are `many free websites
<https://www.google.com/search?q=yaml+validator>`__ that can validate YAML for
you.

You may include comments in your metadata file, which should begin with ``#``.

.. _config-metadata-top-level:

Top-Level Organization
----------------------

Datasets listed within the same metadata file must be given unique names.
Optionally, longer descriptions can be provided too. Details pertaining to each
dataset, including the description, are nested beneath the dataset name using
indentation. You may need to use double quotes around names, descriptions, or
other text if they contains special characters (such as ``:`` or ``#``) or are
composed only of numbers (such as a date).

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
directory. A path to the local copy of this directory must be provided using
the ``data_dir`` key. You may specify ``data_dir`` as an absolute path (e.g.,
``C:\Users\me\folder``) or as a path relative to the YAML file (e.g.,
``folder``).

Paths to individual files within the dataset are provided using keys listed
below. These paths should be given relative to ``data_dir``. If ``data_dir`` is
flat (no subdirectories), these should be simply the file names. Only
``data_file`` is required.

======================  ========================================================
Key                     Description
======================  ========================================================
``data_file``           A single Neo_-compatible data file (required)
``video_file``          A video file that can be synchronized with ``data_file``
``annotations_file``    A CSV file for read-only annotations
``epoch_encoder_file``  A CSV file for annotations writable by the epoch encoder
``tridesclous_file``    A CSV file output by tridesclous_'s DataIO.export_spikes_
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

Data files must be stored on the local computer for **neurotic** to load them
and display their contents. If the files are available for download from a
remote server, **neurotic** can be configured to download them for you to the
local directory specified by ``data_dir`` if the files aren't there already.

Specify the URL to the directory containing the data on the remote server using
``remote_data_dir``. **neurotic** expects the local ``data_dir`` and the
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

With a YAML file like this, the file paths ``data_file`` and ``video_file`` are
appended to ``remote_data_dir`` to obtain the complete URLs for downloading
these files, and they will be saved to the local ``data_dir``.

If you have many datasets hosted by the same server, you can specify the server
URL just once using the special ``remote_data_root`` key, which should be given
outside of any dataset's YAML block with no indentation. This allows you to
provide for each dataset a partial URL to a folder in ``remote_data_dir`` which
is relative to ``remote_data_root``. For example:

.. code-block:: yaml

    remote_data_root: http://myserver

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
to the YAML file. In the example above, if the YAML file is located in
``C:\Users\me``, the paths could be abbreviated:

.. code-block:: yaml

    remote_data_root: http://myserver

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
    file along with a remotely accessible data store such as GIN_ to make your
    metadata file fully portable. The same metadata file could be copied to a
    different computer, and downloaded files will automatically be saved to the
    right place. Data stores can be password protected and **neurotic** will
    prompt you for a user name and password. This makes it easy to share the
    **neurotic** experience with your colleagues! 🤪

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

**neurotic** warns users about the risk of async if ``video_file`` is given but
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

**neurotic** will automatically suggest values for ``video_jumps`` if it reads
an AxoGraph file that contains stops and restarts (only if ``video_jumps`` is
not already specified).

.. _config-metadata-plots:

Plot Parameters
---------------

Use the ``plots`` parameter to specify which signal channels from ``data_file``
you want plotted and how to scale them.

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

            - channel: Intracellular
              ylabel: B3 neuron
              units: mV
              ylim: [-100, 50]

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

The amount of time initially visible can be specified in seconds with
``t_width``.

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

Spikes with peaks that fall within amplitude windows given by
``amplitude_discriminators`` can be automatically detected by **neurotic** on
the basis of amplitude alone. Note that amplitude discriminators are only
applied if fast loading is off (``lazy=False``).

Detected spikes are indicated on the signals with markers, and spike trains are
displayed in a raster plot.

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
              amplitude: [50, 150] # uV

            - name: Unit 2
              channel: Extracellular
              amplitude: [20, 50] # uV
              epoch: Unit 2 activity

Here two units are detected on the same channel with different amplitude
windows. Any peaks between 50 and 150 microvolts on the "Extracellular" channel
will be tagged as a spike belonging to "Unit 1". The discriminator for "Unit 2"
provides the optional ``epoch`` parameter. This restricts detection of "Unit 2"
to spikes within the amplitude window that occur at the same time as epochs
labeled "Unit 2 activity". These epochs can be created by the epoch encoder
(reload required to rerun spike detection at launch-time), specified in the
read-only ``annotations_file``, or even be contained in the ``data_file`` if
the format supports epochs.

Amplitude windows are permitted to be negative.

.. _config-metadata-tridesclous:

tridesclous Spike Sorting Results
---------------------------------

tridesclous_ is a sophisticated spike sorting toolkit. The results of a sorting
process can be exported to a CSV file using tridesclous's DataIO.export_spikes_
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

.. _config-metadata-example:

A Complete Example
------------------

These are the contents of the example metadata file that ships with
**neurotic**, which can be loaded by running ``neurotic`` from the command line
without arguments:

.. literalinclude:: ../neurotic/example/metadata.yml
   :language: yaml


.. _DataIO.export_spikes: https://tridesclous.readthedocs.io/en/latest/api.html#tridesclous.dataio.DataIO.export_spikes
.. _GIN:                  https://gin.g-node.org
.. _Neo:                  https://github.com/NeuralEnsemble/python-neo
.. _tridesclous:          https://github.com/tridesclous/tridesclous
