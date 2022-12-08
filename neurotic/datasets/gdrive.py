# -*- coding: utf-8 -*-
"""
The :mod:`neurotic.datasets.gdrive` module implements a class for downloading
files from Google Drive using paths, rather than file IDs or shareable links.

.. autoclass:: GoogleDriveDownloader
   :members:
"""

import os
import shutil
import urllib
from functools import reduce
from tqdm.auto import tqdm
from pydrive2.auth import GoogleAuth, LoadAuth
from pydrive2.drive import GoogleDrive

import logging
logger = logging.getLogger(__name__)


class GoogleDriveDownloader(GoogleDrive):
    """
    A class for downloading files from Google Drive using paths.

    Files can be specified for download using URL-like paths of the form

        gdrive://<drive name>/<folder 1>/<...>/<folder N>/<file name>

    The "<drive name>" may be "My Drive" for files located in a personal
    Google Drive, or it may be the name of a Shared Drive that the user has
    permission to access.

    Note that these URL-like paths are not equivalent to ordinary URLs
    associated with Google Drive files, such as shareable links, which are
    composed of pseudorandom file IDs and do not reveal anything about the name
    of the file or the folders containing it.

    This class can only download files that are uniquely identifiable by their
    paths. Google Drive does not require file or folder names to be unique, so
    two or more files or folders with identical names may coexist in a folder.
    Such files and folders cannot be distinguished by their paths, so they
    cannot be downloaded using this class. A download will fail while
    traversing the file tree if at any step there is more than one folder or
    file that matches the path.

    This class manages access authorization, optionally saving authorization
    tokens to a file so that the authorization flow does not need to be
    repeated in the future.

    The ``client_secret_file`` should be the path to a client secret file in
    JSON format, obtained from the `Google API Console
    <https://console.developers.google.com/>`_. The Drive API must be enabled
    for the corresponding client.

    If ``save_tokens=False``, the authorization flow (a request via web browser
    for permission to access Google Drive) will always run the first time a new
    instance of this class is used, and authorization will not persist after
    the instance is destroyed. If ``save_tokens=True`` and a file path is
    provided with ``tokens_file``, access/refresh tokens resulting from a
    successful authorization are stored in the file, and tokens are loaded from
    the file in the future, so that the authorization flow does not need to be
    repeated.
    """

    def __init__(self, client_secret_file, tokens_file=None, save_tokens=False):
        """
        Initialize a new GoogleDriveDownloader.
        """

        self.settings = {
            'client_config_file': client_secret_file,
            'oauth_scope': ['https://www.googleapis.com/auth/drive.readonly'],
            'save_credentials': save_tokens,
            'save_credentials_backend': 'file',
            'save_credentials_file': tokens_file
        }

        GoogleDrive.__init__(self, auth=self._create_auth())

    def _create_auth(self):
        """
        Create a GoogleAuth object with the correct settings.
        """
        auth = GoogleAuth()
        auth.settings.update(self.settings)
        return auth

    @LoadAuth
    def authorize(self):
        """
        Obtain tokens for reading the contents of a Google Drive account.

        If ``save_tokens=True``, tokens will be loaded from the ``tokens_file``
        if possible. If tokens cannot be restored this way, or if the loaded
        tokens have expired, an authorization flow will be initiated, prompting
        the user through a web browser to grant read-only privileges to the
        client associated with the ``client_secret_file``. When the
        authorization flow completes, if ``save_tokens=True``, the newly
        created tokens will be stored in the ``tokens_file`` for future use.

        Authorization is performed automatically when needed, but this method
        can be called directly to retrieve (and possibly store) tokens without
        initiating a download.
        """
        # the LoadAuth decorator does all the work
        return

    def deauthorize(self):
        """
        Forget tokens and delete the ``tokens_file``. The authorization flow
        will be required for the next download.
        """
        if os.path.exists(self.settings['save_credentials_file']):
            os.remove(self.settings['save_credentials_file'])
        del self.auth
        self.auth = self._create_auth()

    def is_authorized(self):
        """
        Get the current authorization state.
        """
        return (self.auth is not None and
                self.auth.credentials is not None and
                self.auth.service is not None)

    @LoadAuth
    def GetUserEmail(self):
        """
        Get the email address for the authorized Google Drive account.
        """
        return self.GetAbout()['user']['emailAddress']

    @LoadAuth
    def GetSharedDrivesList(self):
        """
        Return information about available Shared Drives.
        """
        # no PyDrive2 interface for this, so implement it here
        # - TODO: maxResults has default value 10 and upper limit 100. Setting
        #   maxResults=100 is a quick workaround for users with more than 10
        #   Shared Drives but may be insufficient for users with more than 100.
        #   Ideally, this function should iterate through pages of results
        #   exhaustively. Also, this parameter was renamed to pageSize in newer
        #   versions of the API. See API docs here:
        #   https://developers.google.com/drive/api/v3/reference/drives/list
        return self.auth.service.drives().list(maxResults=100).execute(http=self.http)

    def download(self, gdrive_url, local_file, overwrite_existing=False, show_progress=True, bytes_per_chunk=1024*1024*5):
        """
        Download a file from Google Drive using a URL-like path beginning with
        "gdrive://".
        """
        if not overwrite_existing and os.path.exists(local_file):
            logger.info(f'Skipping {os.path.basename(local_file)} (already exists)')
            return

        logger.info(f'Downloading {os.path.basename(local_file)}')
        try:
            self._download_with_progress_bar(gdrive_url, local_file, show_progress=show_progress, bytes_per_chunk=bytes_per_chunk)
        except Exception as e:
            logger.error(f'Skipping {os.path.basename(local_file)} ({e})')
            raise

    def _download_with_progress_bar(self, gdrive_url, local_file, show_progress=True, bytes_per_chunk=1024*1024*5):
        """
        Download while showing a progress bar.
        """
        # TODO: bytes_per_chunk=1024*1024*100 (100 MiB) would match
        # googleapiclient.http.MediaIoBaseDownload's default chunk size and
        # seems to be significantly faster than smaller values, suggesting
        # chunk fetching incurs a large overhead. Unfortunately, such a large
        # chunk size would prevent the progress bar from updating frequently.
        # As a compromise, the chunk size used by this method is just 5 MiB,
        # which is a little larger than is ideal for progress reporting and yet
        # still noticeably slows downloads. Is there a better solution?

        # determine where to temporarily save the file during download
        temp_file = local_file + '.part'
        logger.debug(f'Temporarily downloading to {temp_file}')

        # create the containing directory if necessary
        if not os.path.exists(os.path.dirname(local_file)):
            os.makedirs(os.path.dirname(local_file))

        # locate the Google Drive file
        logger.debug(f'Locating {gdrive_url}')
        file_id = self._get_file_id(gdrive_url)
        logger.debug(f'Found file id {file_id}')
        if file_id is None:
            raise ValueError(f'error locating file on server for account "{self.GetUserEmail()}"')
        file = self.CreateFile({'id': file_id})

        try:
            with tqdm(total=int(file['fileSize']), unit='B', unit_scale=True) as pbar:
                def update_pbar(total_transferred, file_size):
                    pbar.n = total_transferred
                    pbar.update()
                file.GetContentFile(temp_file, callback=update_pbar, chunksize=bytes_per_chunk)

        except:
            # the download is likely incomplete, so delete the temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

            # raise the exception so that it can be handled elsewhere
            raise

        else:
            # download completed, so move the temp file to the final location
            shutil.move(temp_file, local_file)

    def _get_file_id(self, gdrive_url):
        """
        Retrieve the Google Drive ID for the file specified by ``gdrive_url``.
        """
        # verify the url is of the right type
        scheme = urllib.parse.urlparse(gdrive_url).scheme
        if scheme != 'gdrive':
            raise ValueError(f'gdrive_url must begin with "gdrive://": {gdrive_url}')

        # extract drive name ("My Drive" or some Shared Drive) and file path
        drive_name = urllib.parse.urlparse(gdrive_url).netloc
        path = urllib.parse.urlparse(gdrive_url).path
        path = os.path.normpath(path).strip(os.sep).split(os.sep)

        # find the drive id from its name
        if not drive_name:
            raise ValueError('problem parsing drive name')
        elif drive_name == 'My Drive':
            drive_id = 'root'
        else:
            # search for all Shared Drives with a matching name
            drives = self.GetSharedDrivesList().get('items', [])
            drives = [drive for drive in drives if drive['name'] == drive_name]

            # make sure the drive is unique
            if len(drives) == 0:
                raise ValueError(f'drive "{drive_name}" not found on server for account "{self.GetUserEmail()}"')
            elif len(drives) > 1:
                raise ValueError(f'ambigous path, multiple drives with name "{drive_name}" exist on server for account "{self.GetUserEmail()}"')
            else:
                drive_id = drives[0]['id']

        # find the file id from its path by starting at the drive root and
        # recursively searching for the id of the next folder in the path
        file_id = reduce(self._get_child_id, path, drive_id)

        return file_id

    def _get_child_id(self, parent_id, child_name):
        """
        Retrieve the Google Drive ID for the file or folder named
        ``child_name`` located in a folder or drive with ID ``parent_id``.
        """
        # search for all files with a matching name and parent id
        items = self.ListFile({'q': f'title="{child_name}" and "{parent_id}" '
                                    'in parents and trashed=false'}).GetList()

        # make sure the file is unique
        if len(items) == 0:
            raise ValueError(f'file or folder "{child_name}" not found on server for account "{self.GetUserEmail()}"')
        elif len(items) > 1:
            raise ValueError(f'ambiguous path, multiple files or folders with the name "{child_name}" exist under their parent folder on server for account "{self.GetUserEmail()}"')
        else:
            child_id = items[0]['id']

        return child_id
