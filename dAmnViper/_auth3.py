''' dAmnViper.deviantART
    This module is part of the dAmnViper package.
    Created by photofroggy.
'''

import urllib.parse
import urllib.request
import http.cookiejar
    
class ConnectionError(Exception):
    headers = {
        'Location': 'localhost',
        'Status': (0, False),
    }

def fetch_token(obj, username, password, extras={'reusetoken':'1'}, client='dAmnViper (python 3.x) TokenGrabber/2'):
    """This method actually retrieves the cookie and authtoken."""
    extras.update({'username': username, 'password': password})
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
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
    for cookie in jar:
        if cookie.name == 'auth':
            obj.cookie = urllib.parse.unquote(cookie.value)
    # Well, that was nice and easy :D

# EOF
