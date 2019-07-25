|neurotic logo| neurotic
========================

*Curate, visualize, annotate, and share your behavioral ephys data using Python*

|PyPI badge| |GitHub badge| |Docs badge| |Build badge| |Coverage badge|

Documentation_ | `Release Notes`_ | `Issue Tracker`_

**neurotic** is an app for Windows, macOS, and Linux that allows you to easily
review and annotate your electrophysiology data and simultaneously captured
video. It is an easy way to load your Neo_-compatible data into ephyviewer_
without doing any programming. Share a single metadata file with your
colleagues and they too will quickly be looking at the same datasets!

To use the app, first organize your datasets in a *metadata file* like this
(see `Configuring Metadata`_):

.. code-block:: yaml

    my favorite dataset:
        description: This time it actually worked!

        data_dir:           C:\local_dir_containing_files
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

Open your metadata file in **neurotic** and choose a dataset. If the data and
video files aren't already on your local computer, the app can download them
for you, even from a password-protected server. Finally, click launch and the
app will use a standard viewer layout to display your data to you using
ephyviewer_.

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

**Portability is easy with neurotic!** Use relative paths in your metadata file
along with a remotely accessible data store such as GIN_ to make your metadata
file fully portable. The same metadata file can be copied to a different
computer, and downloaded files will automatically be saved to the right place.
Data stores can be password protected and **neurotic** will prompt you for a
user name and password. This makes it easy to share the **neurotic** experience
with your colleagues! 🤪

Installation
------------

**neurotic** requires Python 3.6 or later. It also needs PyAV_, which is most
easily installed using conda_::

    conda install -c conda-forge av

PyAV must be installed manually, but all other dependencies will be installed
with **neurotic**.

Install the latest release version of **neurotic** from PyPI_ using ::

    pip install -U neurotic

or install the latest development version from GitHub_ using ::

    pip install -U git+https://github.com/jpgill86/neurotic.git

Getting Started
---------------

If you installed **neurotic** into a conda environment, first activate it::

    conda activate <environment name>

Launch the app from the command line::

    neurotic

A simple example is provided. Select the "example dataset", download the
associated data (~7 MB), and then click "Launch". See `User Interface`_ for
help with navigation.

Disabling "Fast loading" before launch will enable additional features
including amplitude-threshold spike detection and signal filtering.

To inspect the metadata file associated with the example or to make changes to
it, click "Edit metadata". See `Configuring Metadata`_ for details about the
format.

The command line interface accepts arguments as well:

.. code-block::

    usage: neurotic [-h] [-V] [--no-lazy] [--thick-traces]
                    [--theme {light,dark,original}]
                    [file] [dataset]

    neurotic lets you curate, visualize, annotate, and share your behavioral ephys
    data.

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


.. |neurotic logo| image:: https://raw.githubusercontent.com/jpgill86/neurotic/master/neurotic/gui/icons/img/neurotic-logo-30.png
    :alt: Project logo

.. |PyPI badge| image:: https://img.shields.io/pypi/v/neurotic.svg?logo=python&logoColor=white
    :target: PyPI_
    :alt: PyPI project

.. |GitHub badge| image:: https://img.shields.io/badge/github-source_code-blue.svg?logo=github&logoColor=white
    :target: GitHub_
    :alt: GitHub source code

.. |Docs badge| image:: https://img.shields.io/readthedocs/neurotic/latest.svg?logo=read-the-docs&logoColor=white
    :target: ReadTheDocs_
    :alt: Documentation Status

.. |Build badge| image:: https://img.shields.io/travis/com/jpgill86/neurotic/master.svg?logo=travis-ci&logoColor=white
    :target: Travis_
    :alt: Build status

.. |Coverage badge| image:: https://coveralls.io/repos/github/jpgill86/neurotic/badge.svg?branch=master
    :target: Coveralls_
    :alt: Coverage status

.. |Example screenshot| image:: https://raw.githubusercontent.com/jpgill86/neurotic/master/docs/_static/example-screenshot.png
    :target: https://raw.githubusercontent.com/jpgill86/neurotic/master/docs/_static/example-screenshot.png
    :alt: Screenshot

.. _conda:          https://docs.conda.io/projects/conda/en/latest/user-guide/install/
.. _Configuring Metadata: https://neurotic.readthedocs.io/en/latest/metadata.html
.. _Coveralls:      https://coveralls.io/github/jpgill86/neurotic?branch=master
.. _Documentation:  https://neurotic.readthedocs.io/en/latest
.. _ephyviewer:     https://github.com/NeuralEnsemble/ephyviewer
.. _GIN:            https://gin.g-node.org
.. _GitHub:         https://github.com/jpgill86/neurotic
.. _Issue Tracker:  https://github.com/jpgill86/neurotic/issues
.. _Neo:            https://github.com/NeuralEnsemble/python-neo
.. _PyAV:           https://docs.mikeboers.com/pyav/develop/installation.html
.. _PyPI:           https://pypi.org/project/neurotic
.. _ReadTheDocs:    https://readthedocs.org/projects/neurotic
.. _Release Notes:  https://neurotic.readthedocs.io/en/latest/releasenotes.html
.. _Travis:         https://travis-ci.com/jpgill86/neurotic
.. _User Interface: https://ephyviewer.readthedocs.io/en/latest/interface.html
