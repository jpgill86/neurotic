.. _getting-started:

Getting Started
===============

If you installed **neurotic** into a conda environment, first activate it::

    conda activate <environment name>

Launch the standalone app from the command line::

    neurotic

A simple example is provided. Select the "example dataset", download the
associated data (~7 MB), and then click "Launch". See `User Interface`_ for
help with navigation.

Disabling "Fast loading" before launch will enable additional features
including amplitude-threshold spike detection and signal filtering.

The command line interface accepts arguments as well:

.. code-block:: none

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


.. _User Interface: https://ephyviewer.readthedocs.io/en/latest/interface.html
