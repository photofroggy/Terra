''' dAmnViper.deviantART
    This module is part of the dAmnViper package.
    Created by photofroggy.
'''

import urllib.parse
import urllib.request

class HTTPNoRedirect(urllib.request.HTTPRedirectHandler):
    """HTTP Handler which does not follow redirects."""
    def http_error_302(self, req, fp, code, msg, hdrs):
        return fp
    
class ConnectionError(Exception):
    headers = {
        'Location': 'localhost',
        'Status': (0, False),
    }

def fetch_token(obj, username, password, extras={'reusetoken':'1'}, client='dAmnViper (python 3.x) TokenGrabber/2'):
    """This method actually retrieves the cookie and authtoken."""
    extras.update({'username': username, 'password': password})
    opener = urllib.request.build_opener(HTTPNoRedirect)
    req = urllib.request.Request(
        obj.url,
        urllib.parse.urlencode(extras),
        {'User-Agent': client},
    )
    try:
        obj.response = opener.open(req)
    except IOError as e:
        obj.response = ConnectionError()
        obj.response.headers['Status'] = (e.reason.errno, e.strerror)
        return
    cookie = obj.response.headers.get('Set-Cookie', '')
    obj.cookie = urllib.parse.unquote(cookie)
    # Well, that was nice and easy :D

# EOF
