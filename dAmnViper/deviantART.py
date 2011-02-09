''' dAmn Viper - A Python API for dAmn.
    Copyright (C) 2009  Henry Rapley <froggywillneverdie@msn.com>
    Released under a GNU GPL.
'''

import os
import re

_pyver = float(os.sys.version[:3])
if _pyver >= 2.6 and _pyver < 3:
    from dAmnViper._auth26 import fetch_token
elif _pyver >= 3:
    from dAmnViper._auth3 import fetch_token
else:
    import sys
    sys.stdout.write('>>> Your Python install must be at least Python 2.6!\n')
    sys.stdout.write('>>> Python 3.1 is preferable.\n')
    sys.stdout.flush()
    sys.exit(1)


class Login:
    """This class uses given login data to fetch a deviantART cookie and authtoken."""
    
    url = 'https://www.deviantart.com/users/login'
    destination_url = 'http://www.deviantart.com/users/loggedin'
    bad_login_url = 'http://www.deviantart.com/users/wrong-password'
    
    def __init__(self, username, password, extras={'reusetoken':'1'}, client='dAmnViper (python 3.x) TokenGrabber/2'):
        """ Initialise the object. Fetch and process an authtoken. """
        self.cookie = None
        self.token = None
        self.response = None
        self.status = (0, 'Nothing has happened yet.')
        # Attempt to fetch the authoken!
        fetch_token(self, username, password, extras, client)
        # Process the response!
        if self.response.headers.get('Location') != self.destination_url:
            # Something went wrong! Figure out what it is!
            self.handle()
            return
        self.crop()
    
    def crop(self):
        match = re.search('"([0-9a-f]{32})";', self.cookie)
        if match.group(1) is None:
            self.status = (2, 'Authtoken not given. Not sure why.')
            return
        self.token = match.group(1)
        self.status = (1, 'Authtoken retrieved!')
    
    def handle(self):
        """ Handle a login failure. """
        loc = self.response.headers.get('Location')
        if loc == 'localhost':
            status = self.response.headers.get('Status')
            if status[0] == -2:
                self.status = (3, 'Could not connect to the internet.')
            else:
                self.status = (5, status[1])
            return
        if loc == self.bad_login_url:
            self.status = (4, 'Incorrect username or password provided.')
            return
        self.status = (6, 'Something went wrong. I do not know why.')

# EOF
