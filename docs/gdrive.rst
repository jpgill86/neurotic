.. _gdrive:

Configuring for Google Drive
============================

*neurotic* can download files from Google Drive (see :ref:`gdrive-urls` for
details on how to specify remote URLs). **However, before this capability can
be used, you must complete these manual configuration procedures.**

.. _gdrive-client-secret:

Generating a Client Secret File
-------------------------------

Because of limitations stated in Google's Terms of Service on what
client-identifying credentials may be included with open source desktop
applications, it is not possible for *neurotic* to supply users with an
essential file needed for Google Drive access [1]_. This file is called the
client secret file, and you will need to generate one yourself. The
instructions in this section will walk you through this one-time process. This
is a normal part of setting up PyDrive2_, the library *neurotic* uses for this
feature [2]_.

The file produced by following these steps, ``client_secret.json``, does not
provide access to your Google account, so your account is not compromised if
the file falls into the "wrong hands". However, it does identify you to Google
as the creator of that file whenever *neurotic* uses it to download files; for
this reason, you are discouraged from distributing this file to others, as
abuse of it could cause Google to invalidate it and sanction your account.

Follow these steps to create your client secret file:

1. Visit the Google Cloud Platform project dashboard:

    https://console.cloud.google.com/projectselector2

2. Click the "Create Project" button, and name the new project "neurotic", or
   something similar (the exact name does not matter). Note that you can delete
   unwanted projects later from the `Cloud Resource Manager`_.

3. Once created, you will be taken to a "Getting Started" page for the new
   project. The project name should appear at the top of the page, indicating
   the correct project is selected.

4. Using the search bar at the top of the page, search for and then navigate to
   "Google Drive API". On that page, click the "Enable" button.

5. Using the search bar at the top of the page, search for and then navigate to
   "OAuth consent screen". Complete the form to configure the consent screen
   that will be displayed when authorizing *neurotic* to access your Google
   Drive. The following settings are recommended. Understand that from Google's
   perspective you are the developer of the application which will access
   Google Drive.

    - User type: External
    - App name: "neurotic"
    - User support email: <your email>
    - Developer contact information: <your email>
    - Other optional fields may be left blank
    - Scopes: Search for and add "drive.readonly"
    - Test users: Add email addresses for all Google Drive accounts you would
      like to use with *neurotic*, including the Google account you are using
      to make this project if so desired

6. Using the search bar at the top of the page, search for and then navigate to
   "Credentials". Click the "Create Credentials" button and choose "OAuth
   client ID" from the menu. Set Application Type to "Desktop app". Use the
   name "Desktop client 1".

7. After the OAuth client credentials are created, you will see an entry on the
   Credentials page named "Desktop client 1". Click the download button on the
   far right of the entry to download a JSON file. It will have a name like
   ``client_secret_XXX.apps.googleusercontent.com.json``, where ``XXX`` is a
   long random string.

8. Rename the downloaded file to ``client_secret.json``.

9. Launch *neurotic*. Under the Help menu, click "Open Google Drive credentials
   directory". Move the ``client_secret.json`` file into this folder.

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
   continuing to *neurotic*. You will need to select one of your Google
   accounts that was added as a "test user" when creating the client secret
   file. Other accounts will be denied access.

   .. image:: _static/gdrive-auth-1.png
    :alt: Google Drive authorization flow, step 1
    :width: 300

2. Next you will see a notification that the app has not been verified by
   Google. Your own email address will be listed as the software developer
   because this notice is associated with the client secret file you created.
   The message will also state that the app is being tested (rather than is a
   finalized product) because the project you created for the client secret
   file is private.

   Due to the terms-of-service limitations mentioned earlier, it is not
   possible for *neurotic* to distribute a client secret file that would avoid
   presenting you with this notice. This policy exists because open source
   desktop applications can be modified by anyone with access to the system at
   any time, making it impossible for Google to certify that the mutable app
   has any particular identity and is safe. If you trust the application and
   are willing to proceed, click "Continue".

   .. image:: _static/gdrive-auth-2.png
    :alt: Google Drive authorization flow, step 2
    :width: 300

3. To download files from your Google Drive, *neurotic* needs the privileges to
   access and read those files. Click "Allow" to indicate that you want to
   allow this.

   .. image:: _static/gdrive-auth-3.png
    :alt: Google Drive authorization flow, step 3
    :width: 300

4. Click "Allow" another time to confirm.

   .. image:: _static/gdrive-auth-4.png
    :alt: Google Drive authorization flow, step 4
    :width: 300

5. When you see this message in your browser, you can close it: "The
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

.. [2] See also `PyDrive2 Getting Started
       <https://iterative.github.io/PyDrive2/docs/build/html/quickstart.html#authentication>`_.

.. _PyDrive2: https://pypi.org/project/PyDrive2/

.. _Cloud Resource Manager: https://console.cloud.google.com/cloud-resource-manager
