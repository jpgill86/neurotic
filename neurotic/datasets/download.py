# -*- coding: utf-8 -*-
"""

"""

import os
import urllib
from getpass import getpass
import numpy as np
from tqdm.auto import tqdm

from urllib.request import HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm
from ..datasets.ftpauth import FTPBasicAuthHandler


# install HTTP and FTP authentication handlers, the latter of which also adds
# reliable file size retrieval before downloading
_max_bad_login_attempts = 3
_http_auth_handler = HTTPBasicAuthHandler(HTTPPasswordMgrWithDefaultRealm())
_ftp_auth_handler = FTPBasicAuthHandler()
_opener = urllib.request.build_opener(_http_auth_handler, _ftp_auth_handler)
urllib.request.install_opener(_opener)


def _auth_needed(url):
    """
    Determine whether authentication is needed by attempting to make a
    connection
    """

    # escape spaces and other unsafe characters
    url = urllib.parse.quote(url, safe='/:')

    try:
        # try to connect
        with urllib.request.urlopen(url) as dist:
            # if connection was successful, additional auth is not needed
            return False

    except urllib.error.HTTPError as e:

        if e.code == 401:
            # unauthorized
            return True

        else:
            raise

    except urllib.error.URLError as e:

        # special case for ftp errors
        if e.reason.startswith("ftp error: error_perm("):
            reason = e.reason[23:-2]
            code = int(reason[:3])
        else:
            code = None

        if code in [530, 553]:
            # unauthorized
            return True

        else:
            raise


def _authenticate(url):
    """
    Perform HTTP or FTP authentication
    """

    # escape spaces and other unsafe characters
    url = urllib.parse.quote(url, safe='/:')

    bad_login_attempts = 0
    while True:
        try:
            # try to connect
            with urllib.request.urlopen(url) as dist:
                # if connection was successful, authentication is done
                return True

        except urllib.error.HTTPError as e:

            if e.code == 401:
                # unauthorized -- will try to authenticate with handler
                handler = _http_auth_handler

            else:
                raise

        except urllib.error.URLError as e:

            # special case for ftp errors
            if e.reason.startswith("ftp error: error_perm("):
                reason = e.reason[23:-2]
                code = int(reason[:3])
            else:
                code = None

            if code in [530, 553]:
                # unauthorized -- will try to authenticate with handler
                handler = _ftp_auth_handler

            else:
                raise


        if bad_login_attempts >= _max_bad_login_attempts:
            print('Unauthorized: Aborting login')
            return False
        else:
            if bad_login_attempts == 0:
                print('Authentication required')
            else:
                print(f'Failed login ({bad_login_attempts} of '
                      f'{_max_bad_login_attempts}): Bad login credentials, or '
                      f'else user {user} does not have permission to access '
                      f'{url}')
            bad_login_attempts += 1

            netloc = urllib.parse.urlparse(url).netloc
            host, port = urllib.parse.splitport(netloc)
            user = input(f'User name on {host}: ')
            if not user:
                print('No user given, aborting login')
                return False
            passwd = getpass('Password: ')
            handler.add_password(None, netloc, user, passwd)

def _download(url, local_file, bytes_per_chunk=1024*8, show_progress=True):
    """
    Download after authenticating if necessary
    """

    auth_needed =  _auth_needed(url)
    if auth_needed:
        authenticated = _authenticate(url)

    if not auth_needed or (auth_needed and authenticated):

        # create the containing directory if necessary
        if not os.path.exists(os.path.dirname(local_file)):
            os.makedirs(os.path.dirname(local_file))

        with urllib.request.urlopen(urllib.parse.quote(url, safe='/:')) as dist:
            with open(local_file, 'wb') as f:
                file_size_in_bytes = int(dist.headers['Content-Length'])
                num_chunks = int(np.ceil(file_size_in_bytes/bytes_per_chunk))
                if show_progress:
                    pbar = tqdm(total=num_chunks*bytes_per_chunk, unit='B', unit_scale=True)
                while True:
                    chunk = dist.read(bytes_per_chunk)
                    if chunk:
                        f.write(chunk)
                        if show_progress:
                            pbar.update(bytes_per_chunk)
                    else:
                        break
                if show_progress:
                    pbar.close()


def safe_download(url, local_file, **kwargs):
    """
    Download unless the file already exists locally
    """
    if os.path.exists(local_file):
        print(f'Skipping {os.path.basename(local_file)} (already exists)')
        return

    print(f'Downloading {os.path.basename(local_file)}')
    try:
        _download(url, local_file, **kwargs)

    except urllib.error.HTTPError as e:

        if e.code == 404:
            # not found
            print(f'Skipping {os.path.basename(local_file)} (not found on server)')
            return

        else:
            print(f'Encountered a problem: {e}')
            return

    except urllib.error.URLError as e:

        # special case for ftp errors
        if e.reason.startswith("ftp error: error_perm("):
            reason = e.reason[23:-2]
            code = int(reason[:3])
        else:
            code = None

        if code == 550:
            # no such file or folder, or permission denied
            print(f'Skipping {os.path.basename(local_file)} (not found on server)')
            return

        else:
            print(f'Encountered a problem: {e}')
            return
