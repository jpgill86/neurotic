# -*- coding: utf-8 -*-
"""

"""

import ftplib
import urllib
from urllib.request import FTPHandler, HTTPPasswordMgr
from urllib.parse import splitport, splituser, unquote


class FTPBasicAuthHandler(FTPHandler):
    """
    This subclass of urllib.request.FTPHandler implements basic authentication
    management for FTP connections. Like HTTPBasicAuthHandler, this handler for
    FTP connections has a password manager that it checks for login credentials
    before connecting to a server.

    This subclass also ensures that file size is included in the response
    header, which can fail for some FTP servers if the original FTPHandler is
    used.

    This handler can be installed globally in a Python session so that calls
    to urllib.request.urlopen('ftp://...') will use it automatically:

    >>> handler = FTPBasicAuthHandler()
    >>> handler.add_password(None, uri, user, passwd)  # realm must be None
    >>> opener = urllib.request.build_opener(handler)
    >>> urllib.request.install_opener(opener)
    """

    def __init__(self, password_mgr=None):
        """

        """

        if password_mgr is None:
            password_mgr = HTTPPasswordMgr()
        self.passwd = password_mgr
        self.add_password = self.passwd.add_password
        return super().__init__()

    def ftp_open(self, req):
        """
        When ftp requests are made using this handler, this function gets
        called at some point, and it in turn calls the connect_ftp method. In
        this subclass's reimplementation of connect_ftp, the FQDN of the
        request's host is needed for looking up login credentials in the
        password manager. However, by the time connect_ftp is called, that
        information has been stripped away, and the host argument passed to
        connect_ftp contains only the host's IP address instead of the FQDN.
        This reimplementation of ftp_open, which is little more than a
        copy-and-paste from the superclass's implementation, captures the
        original host FQDN before it is replaced with the IP address and saves
        it for later use.

        This reimplementation also ensures that the file size appears in the
        response header by querying for it directly. For some FTP servers the
        original implementation should handle this (retrlen should contain the
        file size). However, for others this can fail silently due to the
        server response not matching an anticipated regular expression.
        """

        import sys
        import email
        import socket
        from urllib.error import URLError
        from urllib.parse import splitattr, splitpasswd, splitvalue
        from urllib.response import addinfourl

        ####################################################
        #  COPIED FROM FTPHandler.ftp_open (PYTHON 3.6.6)  #
        #  WITH JUST A FEW ADDITIONS                       #
        ####################################################

        import ftplib
        import mimetypes
        host = req.host
        if not host:
            raise URLError('ftp error: no host given')
        host, port = splitport(host)
        if port is None:
            port = ftplib.FTP_PORT
        else:
            port = int(port)

        # username/password handling
        user, host = splituser(host)
        if user:
            user, passwd = splitpasswd(user)
        else:
            passwd = None
        host = unquote(host)
        user = user or ''
        passwd = passwd or ''

        ############################################
        # DIFFERENT FROM FTPHandler.ftp_open
        # save the host FQDN for later
        self.last_req_host = host
        ############################################
        try:
            host = socket.gethostbyname(host)
        except OSError as msg:
            raise URLError(msg)
        path, attrs = splitattr(req.selector)
        dirs = path.split('/')
        dirs = list(map(unquote, dirs))
        dirs, file = dirs[:-1], dirs[-1]
        if dirs and not dirs[0]:
            dirs = dirs[1:]
        try:
            fw = self.connect_ftp(user, passwd, host, port, dirs, req.timeout)
            type = file and 'I' or 'D'
            for attr in attrs:
                attr, value = splitvalue(attr)
                if attr.lower() == 'type' and \
                   value in ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()
            ############################################
            # DIFFERENT FROM FTPHandler.ftp_open
            size = fw.ftp.size(file)
            ############################################
            fp, retrlen = fw.retrfile(file, type)
            headers = ""
            mtype = mimetypes.guess_type(req.full_url)[0]
            if mtype:
                headers += "Content-type: %s\n" % mtype
            if retrlen is not None and retrlen >= 0:
                headers += "Content-length: %d\n" % retrlen
            ############################################
            # DIFFERENT FROM FTPHandler.ftp_open
            elif size is not None and size >= 0:
                headers += "Content-length: %d\n" % size
            ############################################
            headers = email.message_from_string(headers)
            return addinfourl(fp, headers, req.full_url)
        except ftplib.all_errors as exp:
            exc = URLError('ftp error: %r' % exp)
            raise exc.with_traceback(sys.exc_info()[2])

    def connect_ftp(self, user, passwd, host, port, dirs, timeout):
        """
        Unless authentication credentials are provided in the request URL
        (ftp://user:passwd@host/path), this method will be called with empty
        user and passwd arguments. In that case, this reimplementation of
        connect_ftp checks the password manager for credentials matching the
        last_req_host (the host argument will be an IP address instead of the
        FQDN and is thereby useless if the password manager is keyed by FQDN).
        """

        if not user and not passwd:
            user, passwd = self.passwd.find_user_password(None, self.last_req_host)
        return super().connect_ftp(user, passwd, host, port, dirs, timeout)


def setup():
    """
    Install FTPBasicAuthHandler as the global default FTP handler

    Note that install_opener will remove all other non-default handlers
    installed in a different opener, such as an HTTPBasicAuthHandler.
    """

    handler = FTPBasicAuthHandler()
    opener = urllib.request.build_opener(handler)
    urllib.request.install_opener(opener)
    return handler
