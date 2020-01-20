.. _installation:

Installation
============

**neurotic** requires Python 3.6 or later.

Note that the latest release of one of **neurotic**'s dependencies, pyqtgraph
0.10.0, is incompatible with Python 3.8 or later on Windows unless that
dependency is installed via conda-forge (recommended method) (:issue:`details
<129>`).

.. _installation-conda-forge:

Recommended Method: conda-forge
-------------------------------

conda_ users can install **neurotic** and all of its dependencies with one
command::

    conda install -c conda-forge neurotic

On Windows, this will also create a Start Menu shortcut for launching the app.

.. _installation-pip:

Alternate Method: pip
---------------------

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

.. _installation-installers:

Alternate Method: Standalone Installers
---------------------------------------

**This will be the simplest and most convenient installation method for many
users**, especially those uncomfortable with managing Python environments, but
there are a couple caveats.

For users who do not want to independently install Python or conda just to use
**neurotic**, traditional program installers exist. These will install
**neurotic** and everything it needs (including a fully contained Python
environment) into a dedicated directory on your computer. On Windows, the
installer will also create a Start Menu shortcut for launching the app.

If available, these installers can be found on the `GitHub Releases`_ page,
listed under "Assets". However, because the process of building installers is
not yet automated, they may not be available for the latest releases.

Installers are not generally recommended for users who already have a working
Python environment and who are comfortable with ``conda``/``pip`` because the
installers use more disk space and may be less straightforward to upgrade.
Instead, the other methods described above are recommended.

For developers, a recipe for building new installers using `conda constructor`_
is maintained here: `constructor recipe`_.

.. _installation-updating:

Updating neurotic
-----------------

If you installed **neurotic** from conda-forge, you can update it using ::

    conda update -c conda-forge neurotic

If you installed **neurotic** using ``pip``, use ::

    pip install -U neurotic

If you installed **neurotic** using a standalone installer, you can try ::

    conda update -c conda-forge neurotic

but uninstalling and reinstalling using a newer installer may work just as
well.


.. _conda:              https://docs.conda.io/projects/conda/en/latest/user-guide/install/
.. _conda constructor:  https://github.com/conda/constructor
.. _constructor recipe: https://github.com/jpgill86/neurotic-constructor
.. _ephyviewer:         https://github.com/NeuralEnsemble/ephyviewer
.. _GitHub:             https://github.com/jpgill86/neurotic
.. _GitHub Releases:    https://github.com/jpgill86/neurotic/releases
.. _PyAV:               https://docs.mikeboers.com/pyav/develop/overview/installation.html
.. _PyPI:               https://pypi.org/project/neurotic
