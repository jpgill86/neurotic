.. _overview:

Overview
========

To use *neurotic*, first organize your datasets in a *metadata file* like this
(see :ref:`config-metadata`):

.. code-block:: yaml

    my favorite dataset:
        description: This time it actually worked!

        data_dir:           C:\local_dir_containing_files
        remote_data_dir:    http://myserver/remote_dir_containing_downloadable_files  # optional
        data_file:          data.axgx
        video_file:         video.mp4
        # etc

        video_offset: -3.4  # seconds between start of video and data acq
        epoch_encoder_possible_labels:
            - label01
            - label02
        plots:
            - channel: I2
              ylim: [-30, 30]
            - channel: RN
              ylim: [-60, 60]
            # etc

        filters:  # used only if fast loading is off (lazy=False)
            - channel: Force
              lowpass: 50
            # etc
        amplitude_discriminators:  # used only if fast loading is off (lazy=False)
            - name: B3 neuron
              channel: BN2
              units: uV
              amplitude: [50, 100]
            # etc

    another dataset:
        # etc

Open your metadata file in *neurotic* and choose a dataset. If the data and
video files aren't already on your local computer, the app can download them
for you, even from a password-protected server or from Google Drive. Finally,
click launch and the app will use a standard viewer layout to display your data
to you using ephyviewer_.

|Example screenshot|

*In the screenshot above, the video frame shows a voracious sea slug* (Aplysia
californica) *swallowing a strip of unbreakable seaweed attached to a force
transducer. Implanted electrodes recorded from a muscle and the major nerves
controlling feeding. The epoch encoder was used to mark the times when seaweed
moved into the mouth. Spikes corresponding to activity of identified neurons
were detected by* neurotic *using customizable parameters.*

The viewers are easy and intuitive to navigate (see `User Interface`_):

- Pressing the play button will scroll through your data and video in real
  time, or at a higher or lower rate if the speed parameter is changed.
- The arrow/WASD keys allow you to step through time in variable increments.
- Jump to a time by clicking on an event in the event list or a table entry in
  the epoch encoder.
- To show more or less time at once, right-click and drag right or left to
  contract or expand time.
- Scroll the mouse wheel in the trace viewer or video viewer to zoom.
- The epoch encoder can be used to block out periods of time during which
  something interesting is happening for later review or further analysis
  (saved to a CSV file).
- All panels can be hidden, undocked, stacked, or repositioned on the fly.

Electrophysiologists will find this tool useful even if they don't need the
video synchronization feature!

**Portability is easy with neurotic!** Use relative paths in your metadata file
along with a remotely accessible data store such as GIN_ or a Shared Drive on
Google Drive to make your metadata file fully portable. The same metadata file
can be copied to a different computer, and downloaded files will automatically
be saved to the right place. Data stores can be password protected and
*neurotic* will prompt you for a user name and password. This makes it easy to
share the *neurotic* experience with your colleagues! 🤪


.. |Example screenshot| image:: _static/example-screenshot.png
   :target: _static/example-screenshot.png
   :alt: Screenshot

.. _ephyviewer:     https://ephyviewer.readthedocs.io/en/latest
.. _GIN:            https://gin.g-node.org
.. _User Interface: https://ephyviewer.readthedocs.io/en/latest/interface.html
