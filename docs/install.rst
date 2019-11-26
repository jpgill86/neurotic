.. _installation:

Installation
============

**neurotic** requires Python 3.6 or later.

Note that the latest release of one of **neurotic**'s dependencies, pyqtgraph
0.10.0, is incompatible with Python 3.8 or later on Windows unless that
dependency is installed via conda-forge (recommended method) (:issue:`details
<129>`).

.. _installation-conda-forge:

Recommended Method
------------------

conda_ users can install **neurotic** and all of its dependencies with one
command::

    conda install -c conda-forge neurotic

On Windows, this will also create a Start Menu shortcut for launching the app.

.. _installation-pip:

Alternate Method using pip
--------------------------

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


.. _conda:          https://docs.conda.io/projects/conda/en/latest/user-guide/install/
.. _ephyviewer:     https://github.com/NeuralEnsemble/ephyviewer
.. _GitHub:         https://github.com/jpgill86/neurotic
.. _PyAV:           https://docs.mikeboers.com/pyav/develop/overview/installation.html
.. _PyPI:           https://pypi.org/project/neurotic
