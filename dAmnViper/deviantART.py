''' dAmn Viper - A Python API for dAmn.
    Copyright (C) 2009  Henry Rapley <froggywillneverdie@msn.com>
    Released under a GNU GPL.
'''

import os
import re

_pyver = float(os.sys.version[:3])
if _pyver >= 2.6 and _pyver < 3:
    from dAmnViper._auth26 import fetch_cookie
    from dAmnViper._auth26 import fetch_channel
elif _pyver >= 3:
    from dAmnViper._auth3 import fetch_cookie
    from dAmnViper._auth3 import fetch_channel
else:
    import sys
    sys.stdout.write('>>> Your Python install must be at least Python 2.6!\n')
    sys.stdout.write('>>> Python 3.1 is preferable.\n')
    sys.stdout.flush()
    sys.exit(1)


class Login:
    """This class uses given login data to fetch a deviantART cookie and authtoken."""
    
    url = 'https://www.deviantart.com/users/login'
    curl = 'http://chat.deviantart.com/chat/botdom'
    
    def __init__(self, username, password, extras={'remember_me':'1'}, client='dAmnViper (python 3.x) TokenGrabber/2'):
        """ Initialise the object. Fetch and process an authtoken. """
        self.jar = None
        self.cookie = None
        self.token = None
        self.response = None
        self.status = (0, 'Nothing has happened yet.')
        # Attempt to fetch the authoken!
        response = fetch_cookie(self, username, password, extras, client)
        # Process the response!
        url = response.geturl()
        if url == 'ConnectionError' or not 'loggedin=1' in url:
            self.handle(response)
            return
        response = fetch_channel(self, self.curl, client)
        # Process the response!
        url = response.geturl()
        if url == 'ConnectionError' or url != self.curl:
            self.handle(response)
            return
        self.crop(username, response.data)
    
    def crop(self, username, data):
        match = re.search('"'+username+'", "([0-9a-f]{32})"', data, re.IGNORECASE)
        if match is None or match.group(1) is None:
            self.status = (2, 'Authtoken not given. Not sure why.')
            return
        self.token = match.group(1)
        self.status = (1, 'Authtoken retrieved!')
    
    def handle(self, response):
        """ Handle a login failure. """
        loc = response.geturl()
        if 'wrong-password' in loc:
            self.status = (4, 'Incorrect username or password provided.')
            return
        if loc == 'localhost':
            status = response.headers.get('Status')
            if status[0] == -2:
                self.status = (3, 'Could not connect to the internet.')
            else:
                self.status = (5, status[1])
            return
        self.status = (6, 'Something went wrong. I do not know why.')

# EOF
