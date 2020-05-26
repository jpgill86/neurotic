.. _getting-started:

Getting Started
===============

Windows users who installed using a standalone installer or conda_ should be
able to launch *neurotic* from the Start Menu.

Mac and Linux users, as well as Windows users, can use the Terminal, command
line, or Anaconda Prompt to start the app:

1. If you installed *neurotic* into a conda environment, first activate it::

    conda activate <environment name>

   If you used a standalone installer, *neurotic* will have been installed into
   a conda environment named "``neurotic``", so you should use ::

    conda activate neurotic

2. Next, launch the app from the command line by invoking its name::

    neurotic

Several examples are provided. Select one, download the associated data using
the "Download data" menu action, and then click "Launch". See `User Interface`_
for help with navigation.

Disabling "Fast loading" before launch will enable additional features
including amplitude-threshold spike detection and signal filtering.

To inspect the metadata file associated with the examples or to make changes to
it, click "Edit metadata". See :ref:`config-metadata` for details about the
format.

If you like working with Jupyter notebooks, you can launch an example notebook
that includes a tutorial for using *neurotic*'s API::

    neurotic --launch-example-notebook

The command line interface accepts other arguments too:

.. program-output:: neurotic --help


.. _conda:          https://docs.conda.io/projects/conda/en/latest/user-guide/install/
.. _User Interface: https://ephyviewer.readthedocs.io/en/latest/interface.html
