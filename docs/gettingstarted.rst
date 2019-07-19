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

.. program-output:: neurotic --help


.. _User Interface: https://ephyviewer.readthedocs.io/en/latest/interface.html
