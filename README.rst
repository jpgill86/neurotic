neurotic
========

*Curate, visualize, and annotate your behavioral ephys data using Python*

.. image:: https://img.shields.io/pypi/v/neurotic.svg
    :target: PyPI_
    :alt: PyPI project

.. image:: https://img.shields.io/badge/github-source_code-blue.svg
    :target: GitHub_
    :alt: GitHub source code

.. image:: https://travis-ci.com/jpgill86/neurotic.svg?branch=master
    :target: https://travis-ci.com/jpgill86/neurotic
    :alt: Build status

.. image:: https://coveralls.io/repos/github/jpgill86/neurotic/badge.svg?branch=master
    :target: https://coveralls.io/github/jpgill86/neurotic?branch=master
    :alt: Coverage status

.. _PyPI:   https://pypi.org/project/neurotic/
.. _GitHub: https://github.com/jpgill86/neurotic/

Installing dependencies
-----------------------

Because **neurotic** depends on some pre-release changes in a couple libraries,
``pip`` cannot automatically fetch all dependencies during normal installation.
Therefore, **dependencies must be installed manually**.

With conda
~~~~~~~~~~

A recipe for installing **neurotic** via ``conda`` directly is not yet
available. However, the file ``environment.yml`` is provided for installing its
dependencies into a conda environment. To install into a new conda environment
named ``neurotic``, use these commands::

    git clone https://github.com/jpgill86/neurotic.git
    conda env create -f neurotic/environment.yml -n neurotic

To update an existing environment, replace ``conda env create`` with ``conda
env update``.

Remember to switch environments if necessary before proceeding with
installation (``conda activate neurotic`` or ``source activate neurotic``).

Without conda
~~~~~~~~~~~~~

The file ``requirements.txt`` is provided for installing dependencies with
``pip``. Dependencies can be installed using these commands::

    git clone https://github.com/jpgill86/neurotic.git
    pip install -U -r neurotic/requirements.txt

If you get an error while installing PyAV, especially on Windows, you may need
to build it from scratch or get it from another source, such as conda-forge::

    conda install -c conda-forge av

Installing neurotic
-------------------

To reiterate, you must install dependencies manually. They will not be
installed with **neurotic**.

To install the latest release version from PyPI_, use ::

    pip install neurotic

To install the latest development version from GitHub_, use ::

    pip install git+https://github.com/jpgill86/neurotic.git

To install from a local copy of the source code, use ::

    python setup.py install

Getting started
---------------

Launch the standalone app from the command line::

    neurotic

A simple example is provided. Select the "example dataset", download the
associated data, and then click launch.

Questions and support
---------------------

Please post any questions, problems, comments, or suggestions in the `GitHub
issue tracker <https://github.com/jpgill86/neurotic/issues>`_.

Changes
-------

0.1.1
~~~~~

* Fix various downloader errors
  (`#7 <https://github.com/jpgill86/neurotic/pull/7>`__)

0.1.0
~~~~~

* First release
