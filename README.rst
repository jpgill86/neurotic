|neurotic logo| neurotic
========================

*Curate, visualize, annotate, and share your behavioral ephys data using Python*

|PyPI badge| |Anaconda badge| |GitHub badge| |Feedstock badge| |Docs badge| |Travis badge| |Azure badge| |Coverage badge| |Zenodo badge|

Documentation_ | `Release Notes`_ | `Issue Tracker`_

**neurotic** is an app for Windows, macOS, and Linux that allows you to easily
review and annotate your electrophysiology data and simultaneously captured
video. It is an easy way to load your Neo_-compatible data (see neo.io_ for
file formats) into ephyviewer_ without doing any programming. Share a single
metadata file with your colleagues and they too will quickly be looking at the
same datasets!

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
              units: uV
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

**neurotic** requires Python 3.6 or later.

Note that the latest release of one of **neurotic**'s dependencies, pyqtgraph
0.10.0, is incompatible with Python 3.8 or later on Windows unless that
dependency is installed via conda-forge (recommended method) (`details
<https://github.com/jpgill86/neurotic/issues/129>`_).

Recommended Method
..................

conda_ users can install **neurotic** and all of its dependencies with one
command::

    conda install -c conda-forge neurotic

On Windows, this will also create a Start Menu shortcut for launching the app.

Alternate Method using pip
..........................

Installation of **neurotic** via ``pip`` will install nearly all of its
dependencies automatically, with one exception. **neurotic** requires PyAV_,
which is not easily installed with ``pip`` on some systems, especially Windows.
The easiest way to install PyAV is using conda_::

    conda install -c conda-forge av

Install the latest release version of **neurotic** from PyPI_ using ::

    pip install -U neurotic

or install the latest development version from GitHub_ using ::

    pip install -U git+https://github.com/jpgill86/neurotic.git

Note that if you install the development version, you may also need the latest
development version of ephyviewer_, which you can get using ::

    pip install -U git+https://github.com/NeuralEnsemble/ephyviewer.git

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

If you prefer Jupyter notebooks, you can launch an example notebook instead for
experimenting with **neurotic**'s API::

    neurotic --launch-example-notebook

The command line interface accepts other arguments too:

.. code-block::

    usage: neurotic [-h] [-V] [--debug] [--no-lazy] [--thick-traces]
                    [--show-datetime]
                    [--theme {light,dark,original,printer-friendly}]
                    [--launch-example-notebook]
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
      --debug               enable detailed log messages for debugging
      --no-lazy             do not use fast loading (default: use fast loading)
      --thick-traces        enable support for traces with thick lines, which has
                            a performance cost (default: disable thick line
                            support)
      --show-datetime       display the real-world date and time, which may be
                            inaccurate depending on file type and acquisition
                            software (default: do not display)
      --theme {light,dark,original,printer-friendly}
                            a color theme for the GUI (default: light)
      --launch-example-notebook
                            launch Jupyter with an example notebook instead of
                            starting the standalone app (other args will be
                            ignored)

.. |neurotic logo| image:: https://raw.githubusercontent.com/jpgill86/neurotic/master/neurotic/gui/icons/img/neurotic-logo-30.png
    :alt: Project logo

.. |PyPI badge| image:: https://img.shields.io/pypi/v/neurotic.svg?logo=python&logoColor=white
    :target: PyPI_
    :alt: PyPI project

.. |Anaconda badge| image:: https://img.shields.io/conda/vn/conda-forge/neurotic.svg?label=anaconda&logo=anaconda&logoColor=white
    :target: `Anaconda Cloud`_
    :alt: Anaconda Cloud project

.. |GitHub badge| image:: https://img.shields.io/badge/github-source_code-blue.svg?logo=github&logoColor=white
    :target: GitHub_
    :alt: GitHub source code

.. |Feedstock badge| image:: https://img.shields.io/badge/conda--forge-feedstock-blue.svg?logo=conda-forge&logoColor=white
    :target: `conda-forge feedstock`_
    :alt: conda-forge feedstock

.. |Docs badge| image:: https://img.shields.io/readthedocs/neurotic/latest.svg?logo=read-the-docs&logoColor=white
    :target: ReadTheDocs_
    :alt: Documentation status

.. |Travis badge| image:: https://img.shields.io/travis/com/jpgill86/neurotic/master.svg?logo=travis-ci&logoColor=white
    :target: Travis_
    :alt: Travis build status

.. |Azure badge| image:: https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/neurotic-feedstock?branchName=master
    :target: `conda-forge CI`_
    :alt: conda-forge build status

.. |Coverage badge| image:: https://coveralls.io/repos/github/jpgill86/neurotic/badge.svg?branch=master
    :target: Coveralls_
    :alt: Coverage status

.. |Zenodo badge| image:: https://img.shields.io/badge/DOI-10.5281/zenodo.3564990-blue.svg
   :target: Zenodo_
   :alt: Zenodo archive

.. |Example screenshot| image:: https://raw.githubusercontent.com/jpgill86/neurotic/master/docs/_static/example-screenshot.png
    :target: https://raw.githubusercontent.com/jpgill86/neurotic/master/docs/_static/example-screenshot.png
    :alt: Screenshot

.. _Anaconda Cloud: https://anaconda.org/conda-forge/neurotic
.. _conda:          https://docs.conda.io/projects/conda/en/latest/user-guide/install/
.. _conda-forge CI: https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=8417&branchName=master
.. _conda-forge feedstock: https://github.com/conda-forge/neurotic-feedstock
.. _Configuring Metadata: https://neurotic.readthedocs.io/en/latest/metadata.html
.. _Coveralls:      https://coveralls.io/github/jpgill86/neurotic?branch=master
.. _Documentation:  https://neurotic.readthedocs.io/en/latest
.. _ephyviewer:     https://github.com/NeuralEnsemble/ephyviewer
.. _GIN:            https://gin.g-node.org
.. _GitHub:         https://github.com/jpgill86/neurotic
.. _Issue Tracker:  https://github.com/jpgill86/neurotic/issues
.. _Neo:            https://github.com/NeuralEnsemble/python-neo
.. _neo.io:         https://neo.readthedocs.io/en/latest/io.html#module-neo.io
.. _PyAV:           https://docs.mikeboers.com/pyav/develop/overview/installation.html
.. _PyPI:           https://pypi.org/project/neurotic
.. _ReadTheDocs:    https://readthedocs.org/projects/neurotic
.. _Release Notes:  https://neurotic.readthedocs.io/en/latest/releasenotes.html
.. _Travis:         https://travis-ci.com/jpgill86/neurotic
.. _User Interface: https://ephyviewer.readthedocs.io/en/latest/interface.html
.. _Zenodo:         https://doi.org/10.5281/zenodo.3564990
