.. _updating:

Updating *neurotic*
===================

The recommended method of updating *neurotic* depends on the original method of
installation.

If you are unsure what method you used, updating using ``conda`` or ``pip`` is
likely to work. Standalone installers may be safe too, though this could lead
to having multiple version installed simultaneously.

.. _updating-installers:

Updating with Standalone Installers
-----------------------------------

If you previously installed *neurotic* using a standalone installer, you may
install a newer version using another installer, either into a different
directory or by first uninstalling the old version. Installers can be
downloaded from the GitHub Releases page:

    `👉 Download installers here (listed under "Assets") 👈`__

    __ `GitHub Releases`_

Alternatively, if a new installer is not currently available for your platform,
or if you would just like a much faster method, you may use the command line
tools provided by the installer (via the "Anaconda Prompt" on Windows, or the
Terminal on macOS and Linux)::

    conda update -c conda-forge neurotic

.. _updating-conda:

Updating with conda
-------------------

If you installed *neurotic* with `conda`_, you can update to the latest release
using ::

    conda update -c conda-forge neurotic

.. _updating-pip:

Updating with pip
-----------------

If you installed *neurotic* using ``pip``, you can update to the latest release
available on PyPI_ using ::

    pip install -U neurotic

Development Version
-------------------

If you are interested in trying new, unreleased features of *neurotic*, you may
install the latest development version from GitHub_ using ::

    pip install -U git+https://github.com/jpgill86/neurotic.git

Note that if you install the development version, you may also need the latest
development version of ephyviewer_, which you can get using ::

    pip install -U git+https://github.com/NeuralEnsemble/ephyviewer.git


.. _conda:              https://docs.conda.io/projects/conda/en/latest/user-guide/install/
.. _ephyviewer:         https://ephyviewer.readthedocs.io/en/latest
.. _GitHub:             https://github.com/jpgill86/neurotic
.. _GitHub Releases:    https://github.com/jpgill86/neurotic/releases
.. _PyPI:               https://pypi.org/project/neurotic
