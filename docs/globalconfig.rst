.. _global-config:

Changing Default Behavior
=========================

Default parameters used by the command line interface for launching the app,
such as which metadata file to open initially, can be configured using global
configuration settings located in ``.neurotic/neurotic-config.txt`` in your
home directory:

 - Windows: ``C:\Users\<username>\.neurotic\neurotic-config.txt``
 - macOS: ``/Users/<username>/.neurotic/neurotic-config.txt``
 - Linux: ``/home/<username>/.neurotic/neurotic-config.txt``

The file can be opened easily using the "View global config file" menu action.

If this file does not exist when *neurotic* is launched, the following template
is created for you:

.. literalinclude:: ../neurotic/global_config_template.txt
   :language: toml
