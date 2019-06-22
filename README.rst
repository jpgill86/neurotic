neurotic
========

*Curate, visualize, and annotate your behavioral ephys data using Python*

.. image:: https://img.shields.io/pypi/v/neurotic.svg
    :target: https://pypi.org/project/neurotic/
    :alt: PyPI project

.. image:: https://img.shields.io/badge/github-source_code-blue.svg
    :target: https://github.com/jpgill86/neurotic
    :alt: GitHub source code

Installation
------------

Because **neurotic** depends on some pre-release changes in a couple libraries,
pip cannot automatically fetch all dependencies during normal setup. The file
``requirements.txt`` is provided for installing the correct versions of
dependencies. Both **neurotic** and its dependencies can be installed using
these commands::

    git clone https://github.com/jpgill86/neurotic
    cd neurotic
    pip install -r requirements.txt
    pip install .

If you get an error while installing PyAV, try this::

    conda install -c conda-forge av

and then attempt to install the dependencies in ``requirements.txt`` again.

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

0.1.0
~~~~~

* First release
