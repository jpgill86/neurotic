.. _installation:

Installing *neurotic*
=====================

*neurotic* requires Python 3.6 or later.

.. _installation-installers:

Standalone Installers (recommended for beginners)
-------------------------------------------------

Downloadable installers make installing *neurotic* easy for beginners. They can
be downloaded from the GitHub Releases page:

    `👉 Download installers here (listed under "Assets") 👈`__

    __ `GitHub Releases`_

These installers are intended for users who do not want to independently
install Python or conda just to use *neurotic*. They will install *neurotic*
and everything it needs (including a fully contained Python environment) into a
dedicated directory on your computer. On Windows, the installer will also
create a Start Menu shortcut for launching the app.

For developers, a recipe for building new installers using `conda constructor`_
is maintained here: `constructor recipe`_.

.. _installation-conda:

Alternate Method: conda (recommended for Pythonistas)
-----------------------------------------------------

conda_ users can install *neurotic* and all of its dependencies with one
command::

    conda install -c conda-forge neurotic

On Windows, this will also create a Start Menu shortcut for launching the app.

.. _installation-pip:

Alternate Method: pip
---------------------

Install *neurotic* from PyPI_ using ::

    pip install neurotic

Note that installation via ``pip`` skips one dependency: PyAV_, which is
required for displaying videos, and without which *neurotic* will ignore
videos. PyAV is not easily installed with ``pip`` on some systems, especially
Windows. The easiest way to separately install PyAV is using conda_::

    conda install -c conda-forge av


.. _conda:              https://docs.conda.io/projects/conda/en/latest/user-guide/install/
.. _conda constructor:  https://github.com/conda/constructor
.. _constructor recipe: https://github.com/jpgill86/neurotic-constructor
.. _ephyviewer:         https://github.com/NeuralEnsemble/ephyviewer
.. _GitHub:             https://github.com/jpgill86/neurotic
.. _GitHub Releases:    https://github.com/jpgill86/neurotic/releases
.. _PyAV:               https://docs.mikeboers.com/pyav/develop/overview/installation.html
.. _PyPI:               https://pypi.org/project/neurotic
