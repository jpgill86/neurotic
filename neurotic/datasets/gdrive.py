# -*- coding: utf-8 -*-
"""
The :mod:`neurotic.datasets.gdrive` module implements a class for downloading
files from Google Drive using paths, rather than file IDs or shareable links.

.. autoclass:: GoogleDriveDownloader
   :members:
"""

import os
import shutil
import json
import pickle
import urllib
from functools import reduce
from tqdm.auto import tqdm
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import logging
logger = logging.getLogger(__name__)


class GoogleDriveDownloader():
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

    The ``credentials_file`` should be the path to a client secrets file in
    JSON format, obtained from the `Google API
    Console <https://console.developers.google.com/>`_. The Drive API must be
    enabled for the corresponding client.

    If ``save_token=False``, the authorization flow (a request via web browser
    for permission to access Google Drive) will always run the first time a new
    instance of this class is used, and authorization will not persist after
    the instance is destroyed. If ``save_token=True`` and a file path is
    provided with ``token_file``, access/refresh tokens resulting from a
    successful authorization are pickled and stored in the file, and tokens are
    loaded from the file in the future, so that the authorization flow does not
    need to be repeated.
    """

    def __init__(self, credentials_file, token_file=None, save_token=False):
        """
        Initialize a new GoogleDriveDownloader.
        """

        self.credentials_file = credentials_file
        self.token_file = token_file
        self.save_token = save_token

        self._creds = None
        self._service = None

    def authorize(self):
        """
        Obtain tokens for reading the contents of a Google Drive account.

        If ``save_token=True``, tokens will be loaded from the ``token_file``
        if possible. If tokens cannot be restored this way, or if the loaded
        tokens have expired, an authorization flow will be initiated, prompting
        the user through a web browser to grant read-only privileges to the
        client associated with the ``credentials_file``. When the authorization
        flow completes, if ``save_token=True``, the newly created tokens will
        be stored in the ``token_file`` for future use.

        This method is executed automatically when needed, but it can be called
        directly to retrieve (and possibly store) tokens without initiating a
        download.
        """
        if not self._creds:
            creds = None

            # load access and refresh tokens from a file if possible
            if self.save_token and self.token_file and os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    # refresh the tokens if they have expired
                    creds.refresh(Request())
                else:
                    # run the authorization flow, letting the user log in and
                    # grant privileges through a web browser
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(f'missing Google Drive API credentials file "{self.credentials_file}"')
                    scopes = ['https://www.googleapis.com/auth/drive.readonly']
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, scopes)
                    creds = flow.run_local_server(port=0)

                # save the tokens to a file so that the authorization flow can
                # be skipped in the future
                if self.save_token and self.token_file:
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(creds, token)

            self._creds = creds

    def deauthorize(self):
        """
        Forget tokens and delete the ``token_file``. The authorization flow
        will be required for the next download.
        """
        self._creds = None
        self._service = None
        if os.path.exists(self.token_file):
            os.remove(self.token_file)

    def is_authorized(self):
        """
        Get the current authorization state.
        """
        return isinstance(self._creds, Credentials) and self._creds.valid

    def _get_service(self):
        """
        Get an authorized googleapiclient Resource for executing API calls.
        """
        if not self._service:
            if not self.is_authorized():
                self.authorize()
            self._service = build('drive', 'v3', credentials=self._creds)
        return self._service

    def get_user_email(self):
        """
        Get the email address for the authorized Google Drive account.
        """
        results = self._get_service().about().get(fields='user(emailAddress)').execute()
        email = results.get('user', {}).get('emailAddress', 'unknown email')
        return email

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

        except HttpError as e:

            error_code = json.loads(e.args[1]).get('error', {}).get('code', None)

            if error_code == 404:
                # not found
                logger.error(f'Skipping {os.path.basename(local_file)} (not found on server for account "{self.get_user_email()}")')
                raise

            else:
                logger.error(f'Skipping {os.path.basename(local_file)} ({e})')
                raise

        except Exception as e:

            logger.error(f'Skipping {os.path.basename(local_file)} ({e})')
            raise

    def _download_with_progress_bar(self, gdrive_url, local_file, show_progress=True, bytes_per_chunk=1024*1024*5):
        """
        Download while showing a progress bar.
        """
        # TODO: bytes_per_chunk=1024*1024*100 (100 MiB) would match
        # MediaIoBaseDownload's default chunk size and seems to be
        # significantly faster than smaller values, suggesting chunk fetching
        # incurs a large overhead. Unfortunately, such a large chunk size would
        # prevent the progress bar from updating frequently. As a compromise,
        # the chunk size used by this method is just 5 MiB, which is a little
        # larger than is ideal for progress reporting and yet still noticeably
        # slows downloads. Is there a better solution?

        # determine where to temporarily save the file during download
        temp_file = local_file + '.part'
        logger.debug(f'Temporarily downloading to {temp_file}')

        # create the containing directory if necessary
        if not os.path.exists(os.path.dirname(local_file)):
            os.makedirs(os.path.dirname(local_file))

        # locate the Google Drive file
        file_id = self._get_file_id(gdrive_url)
        if file_id is None:
            raise ValueError(f'error locating file on server for account "{self.get_user_email()}"')

        # knowing the file size allows progress to be displayed
        file_size_in_bytes = int(self._get_service().files().get(
            fileId=file_id, supportsAllDrives=True,
            fields='size').execute().get('size', 0))

        try:
            with open(temp_file, 'wb') as f:
                request = self._get_service().files().get_media(fileId=file_id)
                downloader = MediaIoBaseDownload(f, request, chunksize=bytes_per_chunk)
                with tqdm(total=file_size_in_bytes, unit='B', unit_scale=True) as pbar:
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()

                        # set progress to the exact number of bytes downloaded so far
                        pbar.n = status.resumable_progress
                        pbar.update()

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
            # search for all drives with a matching name
            drives = self._get_service().drives().list().execute().get('drives', [])
            drives = [drive for drive in drives if drive['name'] == drive_name]

            # make sure the drive is unique
            if len(drives) == 0:
                raise ValueError(f'drive "{drive_name}" not found on server for account "{self.get_user_email()}"')
            elif len(drives) > 1:
                raise ValueError(f'ambigous path, multiple drives with name "{drive_name}" exist on server for account "{self.get_user_email()}"')
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
        items = self._get_service().files().list(
            supportsAllDrives=True, includeItemsFromAllDrives=True,
            q=f'name="{child_name}" and "{parent_id}" in parents and trashed=false',
            fields="nextPageToken, files(id)").execute().get('files', [])

        # make sure the file is unique
        if len(items) == 0:
            raise ValueError(f'file or folder "{child_name}" not found on server for account "{self.get_user_email()}"')
        elif len(items) > 1:
            raise ValueError(f'ambiguous path, multiple files or folders with the name "{child_name}" exist under their parent folder on server for account "{self.get_user_email()}"')
        else:
            child_id = items[0]['id']

        return child_id
