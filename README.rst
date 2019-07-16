|neurotic logo| neurotic
========================

*Curate, visualize, and annotate your behavioral ephys data using Python*

|PyPI badge| |GitHub badge| |Build badge| |Coverage badge|

**neurotic** is an app that allows you to easily review and annotate your
electrophysiology data and simultaneously captured video. It is an easy way to
load your Neo_-compatible data into ephyviewer_ without doing any programming.

To use the app, first organize your datasets in a YAML file like this:

.. code-block:: yaml

    my favorite dataset:
        description: This time it actually worked!

        data_dir:           C:/local_dir_containing_files
        remote_data_dir:    http://myserver/remote_dir_containing_downloadable_files  # optional
        data_file:          data.axgx
        video_file:         video.mp4
        # etc

        video_offset: -3.4  # seconds between start of video and data acq
        epoch_encoder_possible_labels:
            - label01
            - label02
        plots:
            - channel: I2
              ylim: [-30, 30]
            - channel: RN
              ylim: [-60, 60]
            # etc

        filters:  # used only if fast loading is off (lazy=False)
            - channel: Force
              lowpass: 50
            # etc
        amplitude_discriminators:  # used only if fast loading is off (lazy=False)
            - name: B3 neuron
              channel: BN2
              amplitude: [50, 100]
            # etc

    another dataset:
        # etc

Open your YAML metadata file in **neurotic** and choose a dataset. If the data
and video files aren't already on your local computer, the app can download
them for you. Finally, click launch and the app will use a standard viewer
layout to display your data to you using ephyviewer_.

|Example screenshot|

*(Pictured above is a voracious Aplysia californica in the act of making the
researcher very happy.)*

The viewers are easy and intuitive to navigate (see `User Interface`_):

- Pressing the play button will scroll through your data and video in real
  time, or at a higher or lower rate if the speed parameter is changed.
- The arrow/WASD keys allow you to step through time in variable increments.
- Jump to a time by clicking on an event in the event list or a table entry in
  the epoch encoder.
- To show more or less time at once, right-click and drag right or left to
  contract or expand time.
- Scroll the mouse wheel in the trace viewer or video viewer to zoom.
- The epoch encoder can be used to block out periods of time during which
  something interesting is happening for later review or further analysis
  (saved to a CSV file).
- All panels can be hidden, undocked, stacked, or repositioned on the fly.

Electrophysiologists will find this tool useful even if they don't need the
video synchronization feature!

Installation
------------

**neurotic** requires PyAV_, which is most easily installed from conda-forge_.
It also does not explicitly list its dependencies within the package metadata
(see Notes_), so they must be installed manually.

Install **neurotic**, PyAV, and all other dependencies with these commands
(``pip`` may raise a non-fatal error that can be ignored during installation of
dependencies; see Notes_)::

    conda install -c conda-forge av
    pip install elephant>=0.6.2 ephyviewer>=1.1.0 neo>=0.7.2 numpy packaging pandas pylttb pyqt5 pyyaml quantities tqdm
    pip install neurotic

Getting started
---------------

Launch the standalone app from the command line::

    neurotic

A simple example is provided. Select the "example dataset", download the
associated data, and then click "Launch". See `User Interface`_ for help with
navigation.

Disabling "Fast loading" before launch will enable additional features
including amplitude-threshold spike detection and signal filtering.

The command line interface accepts arguments as well::

    usage: neurotic [-h] [-V] [--no-lazy] [--thick-traces]
                    [--theme {light,dark,original}]
                    [file] [dataset]

    neurotic lets you curate, visualize, and annotate your behavioral ephys data.

    positional arguments:
      file                  the path to a metadata YAML file (default: an example
                            file)
      dataset               the name of a dataset in the metadata file to select
                            initially (default: the first entry in the metadata
                            file)

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         show program's version number and exit
      --no-lazy             do not use fast loading (default: use fast loading)
      --thick-traces        enable support for traces with thick lines, which has
                            a performance cost (default: disable thick line
                            support)
      --theme {light,dark,original}
                            a color theme for the GUI (default: light)

Questions and support
---------------------

Please post any questions, problems, comments, or suggestions in the `GitHub
issue tracker`_.

Notes
-----

Before **neurotic** can be configured to automatically install dependencies, an
`upstream library conflict
<https://github.com/NeuralEnsemble/elephant/issues/236>`__ must be fixed. This
should be resolved soon; until then, dependencies can be installed manually.
This warning may appear but can be ignored because the incompatibility between
these versions is trivial: ``ERROR: elephant 0.6.2 has requirement
neo<0.8.0,<=0.7.1, but you'll have neo 0.7.2 which is incompatible``.

Changes
-------

0.6.0 (2019-07-10)
~~~~~~~~~~~~~~~~~~

Improvements
............

* Add a basic "About neurotic" window with version and website information
  (`#38 <https://github.com/jpgill86/neurotic/pull/38>`__)

* Update logo
  (`#39 <https://github.com/jpgill86/neurotic/pull/39>`__)

* Add keywords and project URLs to package metadata
  (`#40 <https://github.com/jpgill86/neurotic/pull/40>`__)

0.5.1 (2019-07-09)
~~~~~~~~~~~~~~~~~~

Compatibility updates
.....................

* Compatibility update for RawIOs with non-zero offset
  (`#37 <https://github.com/jpgill86/neurotic/pull/37>`__)

0.5.0 (2019-07-06)
~~~~~~~~~~~~~~~~~~

Improvements
............

* Support fast (lazy) loading in Neo < 0.8.0
  (`#35 <https://github.com/jpgill86/neurotic/pull/35>`__)

* Add "git." and conditionally ".dirty" to dev local version identifier
  (`#34 <https://github.com/jpgill86/neurotic/pull/34>`__)

0.4.2 (2019-07-06)
~~~~~~~~~~~~~~~~~~

Bug fixes
.........

* Fix for EstimateVideoJumpTimes regression introduced in 0.4.0
  (`#33 <https://github.com/jpgill86/neurotic/pull/33>`__)

0.4.1 (2019-07-02)
~~~~~~~~~~~~~~~~~~

Compatibility updates
.....................

* Change sources of development versions of dependencies
  (`#32 <https://github.com/jpgill86/neurotic/pull/32>`__)

* Compatibility update for scaling of raw signals
  (`#31 <https://github.com/jpgill86/neurotic/pull/31>`__)

0.4.0 (2019-07-01)
~~~~~~~~~~~~~~~~~~

Improvements
............

* Show epochs imported from CSV files with zero duration in epoch viewer
  (`#27 <https://github.com/jpgill86/neurotic/pull/27>`__)

* Show epochs/events imported from data file in events list/epoch viewer
  (`#28 <https://github.com/jpgill86/neurotic/pull/28>`__)

* Alphabetize epoch and event channels by name
  (`#29 <https://github.com/jpgill86/neurotic/pull/29>`__)

0.3.0 (2019-06-29)
~~~~~~~~~~~~~~~~~~

Improvements
............

* Remove dependency on ipywidgets by making notebook widgets optional
  (`#25 <https://github.com/jpgill86/neurotic/pull/25>`__)

  * Notebook widget classes renamed:
    ``MetadataSelector`` → ``MetadataSelectorWidget``,
    ``EphyviewerConfigurator`` → ``EphyviewerConfiguratorWidget``

* Add app description and screenshot to README
  (`#22 <https://github.com/jpgill86/neurotic/pull/22>`__)

* Promote to beta status
  (`#23 <https://github.com/jpgill86/neurotic/pull/23>`__)

0.2.0 (2019-06-28)
~~~~~~~~~~~~~~~~~~

Improvements
............

* Add basic command line arguments
  (`#14 <https://github.com/jpgill86/neurotic/pull/14>`__)

* Add continuous integration with Travis CI for automated testing
  (`#13 <https://github.com/jpgill86/neurotic/pull/13>`__)

* Add some tests
  (`#15 <https://github.com/jpgill86/neurotic/pull/15>`__,
  `#16 <https://github.com/jpgill86/neurotic/pull/16>`__)

* Migrate example data to GIN
  (`#18 <https://github.com/jpgill86/neurotic/pull/18>`__)

Bug fixes
.........

* Fix crash when downloading from a server that does not report file size
  (`#17 <https://github.com/jpgill86/neurotic/pull/17>`__)

* Raise an exception if a Neo RawIO cannot be found for the data file
  (`#12 <https://github.com/jpgill86/neurotic/pull/12>`__)

0.1.1 (2019-06-22)
~~~~~~~~~~~~~~~~~~

Bug fixes
.........

* Fix various downloader errors
  (`#7 <https://github.com/jpgill86/neurotic/pull/7>`__)

0.1.0 (2019-06-22)
~~~~~~~~~~~~~~~~~~

* First release


.. |neurotic logo| image:: https://raw.githubusercontent.com/jpgill86/neurotic/master/neurotic/gui/icons/img/neurotic-logo-30.png
    :alt: Project logo

.. |PyPI badge| image:: https://img.shields.io/pypi/v/neurotic.svg?logo=python&logoColor=white
    :target: PyPI_
    :alt: PyPI project

.. |GitHub badge| image:: https://img.shields.io/badge/github-source_code-blue.svg?logo=github&logoColor=white
    :target: GitHub_
    :alt: GitHub source code

.. |Build badge| image:: https://travis-ci.com/jpgill86/neurotic.svg?branch=master
    :target: Travis_
    :alt: Build status

.. |Coverage badge| image:: https://coveralls.io/repos/github/jpgill86/neurotic/badge.svg?branch=master
    :target: Coveralls_
    :alt: Coverage status

.. |Example screenshot| image:: https://raw.githubusercontent.com/jpgill86/neurotic/master/images/example-screenshot.png
    :alt: Screenshot

.. _conda-forge:          https://anaconda.org/conda-forge/av
.. _Coveralls:            https://coveralls.io/github/jpgill86/neurotic?branch=master
.. _ephyviewer:           https://github.com/NeuralEnsemble/ephyviewer
.. _GitHub:               https://github.com/jpgill86/neurotic
.. _GitHub issue tracker: https://github.com/jpgill86/neurotic/issues
.. _Neo:                  https://github.com/NeuralEnsemble/python-neo
.. _PyAV:                 https://docs.mikeboers.com/pyav/develop/installation.html
.. _PyPI:                 https://pypi.org/project/neurotic
.. _Travis:               https://travis-ci.com/jpgill86/neurotic
.. _User Interface:       https://ephyviewer.readthedocs.io/en/latest/interface.html
