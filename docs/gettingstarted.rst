.. _getting-started:

Getting Started
===============

If you installed **neurotic** into a conda environment, first activate it::

    conda activate <environment name>

Launch the app from the command line::

    neurotic

Several examples are provided. Select one, download the associated data, and
then click "Launch". See `User Interface`_ for help with navigation.

Disabling "Fast loading" before launch will enable additional features
including amplitude-threshold spike detection and signal filtering.

To inspect the metadata file associated with the examples or to make changes to
it, click "Edit metadata". See :ref:`config-metadata` for details about the
format.

If you prefer Jupyter notebooks, you can launch an example notebook instead,
which includes a tutorial for using **neurotic**'s API::

    neurotic --launch-example-notebook

The command line interface accepts other arguments too:

.. program-output:: neurotic --help


.. _User Interface: https://ephyviewer.readthedocs.io/en/latest/interface.html
