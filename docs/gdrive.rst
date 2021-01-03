.. _gdrive:

Configuring for Google Drive
============================

*neurotic* can download files from Google Drive (see :ref:`gdrive-urls` for
details on how to specify remote URLs). **However, before this capability can
be used, you must complete some manual configuration.**

.. _gdrive-client-secret:

Generating a Client Secret File
-------------------------------

Because of limitations stated in Google's Terms of Service on what
client-identifying credentials may be included with open source desktop
applications, it is not possible for *neurotic* to supply users with an
essential file needed for Google Drive access [1]_. This file is called the
client secret file, and you will need to generate one yourself. The
instructions in this section will walk you through this one-time process.

The file produced by following these steps, ``client_secret.json``, does not
provide access to your Google account, so your account is not compromised if
the file falls into the wrong hands. However, it does identify you to Google as
the creator of that file whenever *neurotic* uses it to download files; for
this reason, you are discouraged from distributing this file to others, as
abuse of it could cause Google to invalidate it and sanction your account.

The steps below take advantage of a tutorial. If you know what you are doing,
you can generate your own client secret file from the `Google API Console`_
instead of using the tutorial, but that procedure is much more complicated. The
tutorial is comparatively easy.

1. Click the following link to open a web page. The web page is a tutorial for
   accessing Google Drive programmatically, as *neurotic* does. You will not
   need to follow the steps of this tutorial, but it does provide a convenient
   shortcut for generating the client secret file.

        https://developers.google.com/drive/api/v3/quickstart/python

2. Click the button labeled "Enable the Drive API" in step 1 of the tutorial.
   You may be prompted to log into Google, and then a series of dialog boxes
   will take you through the configuration process. Follow these steps:

    a. Enter new project name: "neurotic".
    b. Accept terms of service, if necessary.
    c. Click "Next".
    d. Configure your OAuth client: Choose "Desktop app".
    e. Click "Create".
    f. Click "Download Client Configuration", which will download a file called
       ``credentials.json``.
    g. Click "Done".

3. Rename ``credentials.json`` to ``client_secret.json``.

4. Launch *neurotic*. Under the Help menu, click "Open Google Drive credentials
   directory". Move the ``client_secret.json`` file into this folder.

5. Finally, close and restart *neurotic*.

.. _gdrive-authorization:

Authorizing *neurotic* to Access Google Drive
---------------------------------------------

After you have created a client secret file and saved it to the right location,
you can attempt to download files from Google Drive using a properly configured
metadata file (see :ref:`gdrive-urls` for details). When you do this for the
first time, or when you use the "Request Google Drive authorization now" action
under the Help menu, you will need to complete the following steps to authorize
*neurotic* to access your Google Drive:

1. Your web browser will open and ask you to sign into a Google account before
   continuing to "Quickstart". This name comes from the tutorial used to make
   the client secret file.

   .. image:: _static/gdrive-auth-1.png
    :alt: Google Drive authorization flow, step 1
    :width: 300

2. You will be presented with an intimidating warning about the app being
   unverified by Google. You will see your own email listed as the software
   developer because this warning is associated with the client secret file you
   created.

   .. image:: _static/gdrive-auth-2.png
    :alt: Google Drive authorization flow, step 2
    :width: 400

3. Due to the terms-of-service limitations mentioned earlier, it is not
   possible for *neurotic* to distribute a client secret file that would avoid
   presenting you with this warning. This policy exists because open source
   desktop applications can be modified by anyone with access to the system at
   any time, making it impossible for Google to certify that the mutable app
   has any particular identity and is safe. If you trust the application and
   are willing to proceed without Google's stamp of approval, click "Advanced"
   to reveal more text, and then click "Go to Quickstart (unsafe)", which will
   take you past this warning.

   .. image:: _static/gdrive-auth-3.png
    :alt: Google Drive authorization flow, step 3
    :width: 400

4. To download files from your Google Drive, *neurotic* needs the privileges to
   access and read those files. Click "Allow" to indicate that you want to
   allow this. Note that again the app is referred to as "Quickstart" due to
   the settings of the tutorial used to create the client secret file.

   .. image:: _static/gdrive-auth-4.png
    :alt: Google Drive authorization flow, step 4
    :width: 300

5. Click "Allow" another time to confirm. Again, "Quickstart" refers to your
   client secret file, which *neurotic* will use.

   .. image:: _static/gdrive-auth-5.png
    :alt: Google Drive authorization flow, step 5
    :width: 300

6. When you see this message in your browser, you can close it: "The
   authentication flow has completed."

The authorization process should now be complete, and you can begin using
*neurotic* to access and download Google Drive files.

.. _gdrive-save-token:

Making Google Drive Authorization Persistent
--------------------------------------------

By default, authorization persists only until *neurotic* is closed. Each time
*neurotic* is restarted and you want to download from Google Drive again, you
will need to repeat the authorization procedure described above. You can avoid
this by configuring *neurotic* to retain the products of authorization (access
and refresh tokens) indefinitely. See :ref:`global-config` for details on the
global configuration file; by setting the ``save_tokens`` parameter under the
``gdrive`` heading to ``true``, you can minimize the frequency of authorization
requests.

.. warning::

    Enabling ``save_tokens`` is not recommended on systems used by others you
    do not trust. These others will be able to download files from your Google
    Drive using *neurotic* with the same level of ease you experience, and with
    access to the token file they could use it outside of *neurotic* to gain
    read-only access to your Google Drive and your Shared Drives.

.. _gdrive-purge-token:

Purging Google Drive Authorization
----------------------------------

If you need to use a different Google account than the one you previously
authorized *neurotic* to use, or if you had set ``save_tokens=true`` and now
want to remove the persistent access and refresh tokens from your system, you
can use the "Purge Google Drive authorization token" action from the Help menu.
After using this, you will need to complete the authorization procedure again,
and you will have the opportunity to select a different Google account.


.. [1] See `this StackOverflow question
       <https://stackoverflow.com/q/27585412>`_ for an informal discussion.

.. _Google API Console: https://console.developers.google.com
