|neurotic logo| neurotic
========================

*Curate, visualize, and annotate your behavioral ephys data using Python*

|PyPI badge| |GitHub badge| |Build badge| |Coverage badge|

**neurotic** is an app that allows you to easily review and annotate your
electrophysiology data and simultaneously captured video. It is an easy way to
load your Neo_-compatible data into ephyviewer_ without doing any programming.

You organize your data sets in a YAML file like this:

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

Open your file in the app and choose a data set. If the data and video files
aren't already on your local computer, the app can download them for you.
Finally, click launch and the app will use a standard viewer layout to display
your data to you using ephyviewer_.

|Example screenshot|

*(Pictured above is a voracious Aplysia californica making the researcher very
happy.)*

The viewers are easy and intuitive to navigate:

- Pressing the play button will scroll through the data and video in real time,
  or at a higher or lower rate if the speed parameter is changed.
- The arrow/WASD keys allow you to step through time.
- Right-clicking and dragging right or left will contract or expand time to show
  more or less at once.
- Scrolling the mouse wheel in the trace viewer or the video viewer will zoom.
- The "epoch encoder" can be used to block out periods of time during which
  something interesting is happening for later review or further analysis
  (saved to a CSV file).
- All panels can be hidden, undocked, or repositioned on the fly.

Electrophysiologists should still find this tool useful even if they don't need
video synchronization.

Installing dependencies
-----------------------

Because **neurotic** depends on some pre-release changes in a couple libraries,
``pip`` cannot automatically fetch all dependencies during normal installation.
Therefore, **dependencies must be installed manually**.

With conda
~~~~~~~~~~

A recipe for installing **neurotic** via ``conda`` directly is not yet
available. However, the file ``environment.yml`` is provided for installing its
dependencies into a conda environment. To install into a new conda environment
named ``neurotic``, use these commands::

    git clone https://github.com/jpgill86/neurotic.git
    conda env create -f neurotic/environment.yml -n neurotic

To update an existing environment, replace ``conda env create`` with ``conda
env update``.

Remember to switch environments if necessary before proceeding with
installation (``conda activate neurotic`` or ``source activate neurotic``).

Without conda
~~~~~~~~~~~~~

The file ``requirements.txt`` is provided for installing dependencies with
``pip``. Dependencies can be installed using these commands::

    git clone https://github.com/jpgill86/neurotic.git
    pip install -U -r neurotic/requirements.txt

If you get an error while installing PyAV, especially on Windows, you may need
to build it from scratch or get it from another source, such as conda-forge::

    conda install -c conda-forge av

Installing neurotic
-------------------

To reiterate, you must install dependencies manually. They will not be
installed with **neurotic**.

To install the latest release version from PyPI_, use ::

    pip install neurotic

To install the latest development version from GitHub_, use ::

    pip install git+https://github.com/jpgill86/neurotic.git

To install from a local copy of the source code, use ::

    python setup.py install

Getting started
---------------

Launch the standalone app from the command line::

    neurotic

A simple example is provided. Select the "example dataset", download the
associated data, and then click launch.

Command line arguments can be listed using ::

    neurotic --help

Questions and support
---------------------

Please post any questions, problems, comments, or suggestions in the `GitHub
issue tracker <https://github.com/jpgill86/neurotic/issues>`_.

Changes
-------

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
    :target: https://travis-ci.com/jpgill86/neurotic
    :alt: Build status

.. |Coverage badge| image:: https://coveralls.io/repos/github/jpgill86/neurotic/badge.svg?branch=master
    :target: https://coveralls.io/github/jpgill86/neurotic?branch=master
    :alt: Coverage status

.. |Example screenshot| image:: https://raw.githubusercontent.com/jpgill86/neurotic/master/images/example-screenshot.png
    :alt: Screenshot

.. _PyPI:       https://pypi.org/project/neurotic
.. _GitHub:     https://github.com/jpgill86/neurotic
.. _ephyviewer: https://github.com/NeuralEnsemble/ephyviewer
.. _Neo:        https://github.com/NeuralEnsemble/python-neo
