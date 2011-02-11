''' dAmnViper.deviantART
    This module is part of the dAmnViper package.
    Created by photofroggy.
'''

import urllib
import urllib2
import cookielib
    
class ConnectionError(Exception):
    headers = {
        'Location': 'localhost',
        'Status': (0, False),
    }
 
def fetch_token(obj, username, password, extras={'reusetoken':'1'}, client='dAmnViper (python 2.x) TokenGrabber/2'):
    """This method actually retrieves the cookie and authtoken."""
    extras.update({'username': username, 'password': password})
    jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    req = urllib2.Request(
        obj.url,
        urllib.urlencode(extras),
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
            obj.cookie = urllib.unquote(cookie.value)
            return
    # Well, that was nice and easy :D

# EOF
