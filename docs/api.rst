.. _api:

API Reference Guide
===================

In addition to using *neurotic* as a standalone app, you can also leverage its
API in your own code.

.. note::

    **TL;DR**: The easiest way to use *neurotic* in an interactive session or
    script is by invoking :func:`neurotic.quick_launch()
    <neurotic.scripts.quick_launch>`. For example:

    >>> metadata = {'data_file': 'data.axgx'}
    >>> neurotic.quick_launch(metadata=metadata)

    or

    >>> neurotic.quick_launch(blk=my_neo_block)

The core of the API consists of two classes and one function:

* :class:`neurotic.datasets.metadata.MetadataSelector`: Read metadata files, download datasets
* :func:`neurotic.datasets.data.load_dataset`: Read datasets, apply filters and spike detection
* :class:`neurotic.gui.config.EphyviewerConfigurator`: Launch ephyviewer

All public package contents are automatically imported directly into the
``neurotic`` namespace. This means that a class like
``neurotic.datasets.metadata.MetadataSelector`` can be accessed more compactly
as ``neurotic.MetadataSelector``.


.. toctree::
   :maxdepth: 1
   :caption: Datasets

   api/data
   api/download
   api/ftpauth
   api/gdrive
   api/metadata


.. toctree::
  :maxdepth: 1
  :caption: GUI

  api/config
  api/epochencoder
  api/notebook
  api/standalone

.. toctree::
  :maxdepth: 1
  :caption: Other

  api/scripts
  api/_elephant_tools
