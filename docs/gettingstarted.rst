.. _getting-started:

Getting Started
===============

Windows users who installed using a standalone installer or conda_ should be
able to launch *neurotic* from the Start Menu.

Mac and Linux users, as well as Windows users, can use the Terminal, command
line, or Anaconda Prompt to start the app:

1. Depending on your operating system, installation method, and environment
   settings, you may be able to just launch the app from the command line by
   invoking its name::

    neurotic

2. If the command is not recognized, you likely need to first activate the
   conda environment into which the app was installed::

    conda activate <environment name>

   If you used a standalone installer, the environment name may be
   "``neurotic``", so you would use ::

    conda activate neurotic

   You can then try again invoking the app name::

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
