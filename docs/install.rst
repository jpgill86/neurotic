.. _installation:

Installation
============

**neurotic** requires Python 3.6 or later. It also needs PyAV_, which is most
easily installed using conda_::

    conda install -c conda-forge av

PyAV must be installed manually, but all other dependencies will be installed
with **neurotic**.

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
.. _PyAV:           https://docs.mikeboers.com/pyav/develop/installation.html
.. _PyPI:           https://pypi.org/project/neurotic
