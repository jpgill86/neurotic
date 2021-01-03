.. _global-config:

Changing Default Behavior
=========================

Default parameters used by the app and by the command line interface, such
as which metadata file to open initially or whether Google Drive access tokens
should be stored indefinitely, can be configured using global configuration
settings located in ``.neurotic/neurotic-config.txt`` in your home directory:

 - Windows: ``C:\Users\<username>\.neurotic\neurotic-config.txt``
 - macOS: ``/Users/<username>/.neurotic/neurotic-config.txt``
 - Linux: ``/home/<username>/.neurotic/neurotic-config.txt``

The file can be opened easily using the "View global config file" menu action.
You may edit it to customize your settings. The next time you launch the app or
use the command line interface, your changes should be in effect.

If this file does not exist when *neurotic* is launched, the following template
is created for you:

.. literalinclude:: ../neurotic/global_config_template.txt
   :language: toml
