.. _install:

Installation
============

**neurotic** requires PyAV_, which is most easily installed from conda-forge_.
It also does not explicitly list its dependencies within the package metadata
[1]_, so they must be installed manually.

To install PyAV and all other dependencies, use these commands (``pip`` may
raise a non-fatal error that can be ignored; see [2]_)::

    conda install -c conda-forge av
    pip install "elephant>=0.6.2" "ephyviewer>=1.1.0" "neo>=0.7.2" numpy packaging pandas pylttb pyqt5 pyyaml quantities tqdm

Finally, install the latest release version of **neurotic** from PyPI_, using
::

    pip install -U neurotic

or install the latest development version from GitHub_ using ::

    pip install -U git+https://github.com/jpgill86/neurotic.git


.. [1] Before **neurotic** can be configured to automatically install
       dependencies, an `upstream library conflict`_ must be fixed. This should
       be resolved soon; until then, dependencies can be installed manually.

.. [2] The following warning may appear during dependency installation but can
       be ignored because the incompatibility between these versions is
       trivial: ``ERROR: elephant 0.6.2 has requirement neo<0.8.0,<=0.7.1, but
       you'll have neo 0.7.2 which is incompatible``. This is related to the
       `upstream library conflict`_ previously mentioned.


.. _conda-forge:    https://anaconda.org/conda-forge/av
.. _GitHub:         https://github.com/jpgill86/neurotic
.. _PyAV:           https://docs.mikeboers.com/pyav/develop/installation.html
.. _PyPI:           https://pypi.org/project/neurotic
.. _upstream library conflict: https://github.com/NeuralEnsemble/elephant/issues/236
