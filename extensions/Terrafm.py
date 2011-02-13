''' This is an experiment with last.fm's API!
    WOOO!
'''

import json
import urllib.request
from threading import Timer
from terra import extension

class Extension(extension.API):
    
    # Configure the extension!
    about = 'Last.fm extension for Terra!'
    version = 1
    author = 'photofroggy'
    
    def init(self):
        # Storage variables! Woooo!
        self.api = api('009dcbb056172eeef7b938f24a7a7eb3')
        self.auto = [False, '', self.cconfig.autojoin, self.cconfig.info.owner, 10]
        self.alt = {}
        # command info
        info = [
            'Use this command to find out what someone is listening to. Powered by last.fm.',
            'Use this command to view the tracks recently listened to by someone. Powered by last.fm.',
            'Use this to compare music tastes of two different users. Powered by last.fm.',
            'Use this to change the settings for autonp. Powered by last.fm.',
            'Use this command to view and set the account you use on last.fm.',
        ]
        # Extension bindings
        self.bind(self.c_nowplaying, 'command', [['nowplaying', 'np']], info[0])
        self.bind(self.c_fmrecent, 'command', ['fmrecent'], info[1])
        self.bind(self.c_tasteometer, 'command', ['tasteometer'], info[2])
        self.bind(self.c_autonp, 'command', [['autonp', 'anp'], 'Owner'], info[3])
        self.bind(self.c_fmname, 'command', ['fmname'], info[4])
        # Events?
        self.bind(self.loads, 'ready')
        self.bind(self.e_unload, 'quit')
        self.bind(self.e_unload, 'reloading')
        # Need to check some shit.
        self.locker()
    
    def c_fmname(self, cmd, dAmn):
        arg = cmd.arguments(1).lower()
        if not arg in ('set', 'list'):
            name = cmd.user.lower() if len(arg) == 0 else arg
            fmname = self.alt.get(name, name)
            msg = cmd.user + ': Using the name "' + fmname + '" for ' + name + '.<br/><sub>'
            msg+= 'Use <b>' + dAmn.trigger + 'fmname set <name></b> to set <b><name></b> as your last.fm name.</sub>'
            dAmn.say(cmd.ns, msg)
            return
        if arg == 'list':
            known = ', '.join(['<abbr title="{0}">{1}</abbr>'.format(account, self.alt[account]) for account in self.alt])
            if known == '':
                dAmn.say(cmd.ns, '{0}: There are no last.fm accounts stored.'.format(cmd.user))
                return
            foot = 'Hover for the dA account associated with the last.fm account.'
            dAmn.say(cmd.ns, '<abbr title="{0}"></abbr><b>Known last.fm accounts:</b><br/><sup>-- {1}<br/>{2}'.format(cmd.user, known, foot))
            return
        name = cmd.arguments(2)
        if name == '':
            dAmn.say(cmd.ns, cmd.user + ': Use <b>' + dAmn.trigger + 'fmname set <name></b> to set <b><name></b> as your last.fm name.')
            return
        if cmd.user.lower() == name.lower():
            dAmn.say(cmd.ns, cmd.user + ': There\'s no point in storing your last.fm name if it is the same as your dA username.')
            return
        self.alt[cmd.user.lower()] = name
        self.saves()
        dAmn.say(cmd.ns, cmd.user + ': Using ' + name + ' as your last.fm username.')
        return
    
    def c_nowplaying(self, cmd, dAmn):
        arg = cmd.arguments(1)
        arg = cmd.user if not arg else arg
        arg = self.alt.get(arg.lower(), arg)
        current = self.api.current(arg)
        if type({}) == type(current):
            if current['message'] != 'No song currently playing.':
                dAmn.say(cmd.ns, cmd.user+': warning, got error: '+current['message'])
                return
            dAmn.say(cmd.ns, cmd.user+': '+arg+' is not playing a song.')
            return
        uslink = '<a href="http://www.last.fm/user/'+arg+'">'+arg+'</a>'
        msg = ['<abbr title="'+cmd.user+'"></abbr><b>'+uslink+' is listening to:</b><sub>']
        msg.append('- <i><b>'+current[1]+'</b> by <b>'+current[0]+'</b></i>')
        if current[2]:
            msg.append('- <b>album:</b> <i>'+current[2]+'</i>')
        dAmn.say(cmd.ns, '<br/>'.join(msg)+'</sub>')
    
    def c_fmrecent(self, cmd, dAmn):
        arg = cmd.arguments(1)
        arg = cmd.user if not arg else arg
        arg = self.alt.get(arg.lower(), arg)
        offset = cmd.arguments(2)
        if bool(offset):
            offset = 2 if not offset.isdigit() else int(offset)
            offset = 1 if offset < 0 else offset
            offset = 10 if offset > 10 else offset
        else:
            offset = 2
        recent = self.api.user.getRecentTracks(arg, offset+1)
        if 'error' in recent:
            dAmn.say(cmd.ns, cmd.user+': Warning, got error: '+recent['message'])
            return
        texts = []
        minus = 0
        if type(recent['recenttracks']['track']) == type([]):
            for index, track in enumerate(recent['recenttracks']['track']):
                if index == 0:
                    if '@attr' in track and 'nowplaying' in track['@attr']:
                        if track['name'] == recent['recenttracks']['track'][index+1]['name']:
                            minus+= 1
                            continue
                if (index-minus) < offset:
                    texts.append(str((index+1)-minus)+'. <i><b>'+track['name'])
                    texts[index-minus]+= '</b> by '+track['artist']['#text']+'</i>.'
        else:
            texts = ['1. <i><b>'+recent['recenttracks']['track']['name']]
            texts[0]+= '</b> by '+recent['recenttracks']['track']['artist']['#text']+'</i>.'
        num = len(texts)
        headl = '<a href="http://www.last.fm/user/'+arg+'">'+arg+'</a>'
        head = '<abbr title="'+cmd.user+'"></abbr><b>'+headl+'\'s '
        head+= ('most recent track:</b>' if num == 1 else 'last '+str(num)+' tracks:</b>')+'<sub>'
        dAmn.say(cmd.ns, head+'<br/>'+('<br/>'.join(texts))+'</sub>')
    
    def c_tasteometer(self, cmd, dAmn):
        arg1 = cmd.arguments(1)
        arg2 = cmd.arguments(2)
        if not arg1:
            dAmn.say(cmd.ns, cmd.user+': You need to provide at least one last.fm username.')
            return
        arg2 = arg2 if arg2 else self.alt.get(cmd.user.lower(), cmd.user)
        if arg1.lower() == arg2.lower():
            dAmn.say(cmd.ns, cmd.user + ': You can only compare different users!')
            return
        limt = cmd.arguments(3)
        if limt:
            limt = 2 if not limt.isdigit() else int(limt)
            limt = 1 if limt < 1 else (10 if limt > 10 else limt)
        else:
            limt = 2
        data = self.api.compare(arg1, arg2, limt)
        if 'error' in data:
            dAmn.say(cmd.ns, cmd.user+': Warning, got error: '+data['message'])
            return
        usrs = data[0]
        score = int(float(data[1])*100)
        match = data[2]
        matches = len(match)
        usls = ['<a href="'+v[1]+'">'+v[0]+'</a>' for v in usrs]
        head = '<abbr title="'+cmd.user+'"></abbr><b>last.fm: '+usls[0]+' </b>vs.<b> '+usls[1]+':</b>'
        del usls
        head+= ' '+str(score)+'% match!<br/>'
        head+= '<b>'+str(matches)+' of the matched artists!</b><br/><sub>' if matches else ''
        del score
        mast = []
        for i, d in enumerate(match):
            link = '<a href="'+d[1]+'">'+d[0]+'</a>'
            mast.append('<i>'+link+'</i>')
        if matches: del link
        del matches
        dAmn.say(cmd.ns, head+'- '+(', '.join(mast))+'</sub>')
        
    def c_autonp(self, cmd, dAmn):
        arg = cmd.arguments(1).lower()
        if arg in ('on', 'off'):
            if self.auto[0] == (arg == 'on'):
                dAmn.say(cmd.ns, cmd.user+': Autonp is already '+('on' if arg == 'on' else 'off')+'.')
                return
            self.auto[0] = arg == 'on'
            if arg == 'off':
                self.auto[1] = ''
            self.saves()
            dAmn.say(cmd.ns, cmd.user+': Turned autonp '+('on' if arg == 'on' else 'off')+'.')
            if arg == 'on':
                self.e_autonp(dAmn)
            return
        if arg == 'set':
            suba = cmd.arguments(2).lower()
            if not suba:
                dAmn.say(cmd.ns, cmd.user+': With this command you can set your last.fm <b>account</b> and the <b>interval</b> between checks.')
                return
            if suba == 'account':
                account = cmd.arguments(3, True)
                if account:
                    self.auto[3] = account
                    self.saves()
                    dAmn.say(cmd.ns, cmd.user+': Set your last.fm account to '+account+'.')
                    return
                dAmn.say(cmd.ns, cmd.user+': Use this to set your last.fm account.')
                return
            if suba == 'interval':
                inter = cmd.arguments(3)
                if not inter:
                    dAmn.say(cmd.ns, cmd.user+': Use this to set the interval between last.fm checks.')
                    return
                if not (inter.isdigit() and int(inter) > 9):
                    dAmn.say(cmd.ns, cmd.user+': The interval must be a number above 9 seconds.')
                    return
                self.auto[4] = int(inter)
                self.saves()
                dAmn.say(cmd.ns, cmd.user+': Set the interval to '+inter+' seconds.')
                return
        if arg in ('chans', 'channels', 'chats', 'chatrooms'):
            msg = ['<abbr title="'+cmd.user+'"></abbr><b>Autonp shows messages in the following channels:</b>']
            msg.append('<sub> - '+(', '.join([dAmn.deform_ns(i) for i in self.auto[2]]))+'</sub>')
            dAmn.say(cmd.ns, '<br/>'.join(msg))
            return
        if arg in ('chan', 'channel', 'chat', 'chatroom'):
            suba = cmd.arguments(2).lower()
            if suba in ('add', 'rem', 'remove'):
                chan = dAmn.deform_ns(cmd.arguments(3))
                if chan:
                    for k, i in enumerate(self.auto[2]):
                        if dAmn.deform_ns(i).lower() == chan.lower():
                            if suba is 'add':
                                dAmn.say(cmd.ns, cmd.user+': '+chan+' is already  in the list.')
                                return
                            self.auto[2].pop(k)
                            self.saves()
                            dAmn.say(cmd.ns, cmd.user+': Removed '+chan+' from the list.')
                            return
                    if suba in ('rem', 'remove'):
                        dAmn.say(cmd.ns, cmd.user+': '+chan+' is not in the list.')
                        return
                    self.auto[2].append(chan)
                    self.saves()
                    dAmn.say(cmd.ns, cmd.user+': Added '+chan+' to the list.')
                    return
            dAmn.say(cmd.ns, cmd.user+': Use this command to <b>add</b> or <b>remove</b> a channel from the list.')
            return
        msg = '<abbr title="{0}"></abbr><b>Autonp is currently switched {1}!</b><br/>'.format(cmd.user, 'on' if self.auto[0] else 'off')
        msg+= '<sup><b>Last.fm Account:</b> {0}<b>;'.format(self.auto[3])
        msg+= ' Interval:</b> {0}<b>;</b></sup>'.format(self.auto[4])
        dAmn.say(cmd.ns, msg)

    def e_autonp(self, dAmn):
        if hasattr(self, 'autotimer'):
            self.autotimer.cancel()
        if not self.auto[0]:
            return
        self.autotimer = Timer(self.auto[4], self.e_autonp, [dAmn])
        self.autotimer.start()
        current = self.api.current(self.auto[3])
        if type({}) == type(current):
            if current['message'] == 'No song currently playing.':
                self.auto[1] = ''
                self.saves()
            return
        if self.auto[1] != '':
            if self.auto[1] == current[1]:
                return
        self.auto[1] = current[1]
        self.saves()
        uslink = '<a href="http://www.last.fm/user/'+self.auto[3]+'">'+self.Bot.owner+'</a>'
        msg = ['<b>'+uslink+' is listening to:</b><sub>']
        msg.append('- <i><b>'+current[1]+'</b> by <b>'+current[0]+'</b></i>')
        if current[2]:
            msg.append('- <b>album:</b> <i>'+current[2]+'</i>')
        for chan in self.auto[2]:
            for c in dAmn.channel.keys():
                if c.lower() == dAmn.format_ns(chan).lower():
                    dAmn.say(dAmn.format_ns(chan), '<br/>'.join(msg)+'</sub>')
    
    def e_unload(self, e, dAmn):
        if hasattr(self, 'autotimer'):
            self.autotimer.cancel()
    
    def loads(self, e, dAmn):
        self.auto = self.storage.loads('auto')
        if not self.auto:
            self.auto = [False, '', self.cconfig.autojoin, self.cconfig.info.owner, 10]
        if hasattr(self, 'autotimer'):
            self.autotimer.cancel()
        if self.auto[0]:
            self.autotimer = Timer(self.auto[4], self.e_autonp, [dAmn])
            self.autotimer.start()
        self.alt = self.storage.loads('alts')
        if self.alt is None:
            self.alt = {}
    
    def saves(self):
        self.storage.dumps('auto', self.auto)
        self.storage.dumps('alts', self.alt)
    
class api:
    """A simple but useful API for last.fm, using their API."""
    
    class resource:
        key = None
        root = 'http://ws.audioscrobbler.com/2.0/?'
    
    def __init__(self, key, root='http://ws.audioscrobbler.com/2.0/?'):
        # Store info!
        self.resource.key = key
        self.resource.root = root
        # API components!
        self.tasteometer = tasteometer(self)
        self.user = fm_user(self)
    
    # <---- BASIC REQUEST FUNCTION ---->
    def request(self, request):
        """Send a request to the last.fm API."""
        data = urllib.request.urlopen(self.resource.root+request+'&api_key='+self.resource.key+'&format=json').read().decode('utf-8', 'ignore')
        return json.JSONDecoder().decode(data)
        
    # <---- CUSTOM API METHODS ---->
    def current(self, user):
        data = self.user.getRecentTracks(user, 1)
        if 'error' in data:
            return data
        if len(data['recenttracks']['track']) < 1:
            return {'error':'foo', 'message':'No song currently playing.'}
        try:
            track = data['recenttracks']['track'][0]
        except KeyError as e:
            track = data['recenttracks']['track']
        if not '@attr' in track or not 'nowplaying' in track['@attr']:
            return {'error':'foo', 'message':'No song currently playing.'}
        return [
            track['artist']['#text'],
            track['name'],
            track['album']['#text']
        ]
    
    def compare(self, user1, user2, limit=5):
        data = self.tasteometer.compare('user', 'user', user1, user2, limit)
        if 'error' in data:
            return data
        matched = (1,)
        res = data['comparison']['result']
        if 'artists' in res and 'artist' in res['artists']:
            if not 'name' in data['comparison']['result']['artists']['artist']:
                matches = data['comparison']['result']['artists']['artist']
                for i in range(0, limit):
                    if len(matches) <= i:
                        continue
                    if matched[0] == 1:
                        matched = ((matches[i]['name'], matches[i]['url']),)
                    else:
                        matched+= ((matches[i]['name'], matches[i]['url']),)
                del matches
            else:
                matched = ((
                        data['comparison']['result']['artists']['artist']['name'],
                        data['comparison']['result']['artists']['artist']['url']
                ))
        else: matched = []
        usr = (1,)
        for i in [0, 1]:
            if not i:
                usr = (
                    (data['comparison']['input']['user'][i]['name'],
                    data['comparison']['input']['user'][i]['url']),
                )
            else:
                usr+= (
                    (data['comparison']['input']['user'][i]['name'],
                    data['comparison']['input']['user'][i]['url']),
                )
        return (usr, data['comparison']['result']['score'], matched)

    # <---- /CUSTOM API METHODS ---->

# <---- API COMPONENTS ---->
#     The following classes
#    provide Python methods
#    which can be used to
#     interact with last.fm's
#    web API.

# <---- TASTEOMETER METHODS ---->
class tasteometer:
    """API tasteometer methods."""

    def __init__(self, api):
        self._request = api.request
        
    def compare(self, type1, type2, value1, value2, limit=5):
        """Get a Tasteometer score."""
        return self._request(
            'method=tasteometer.compare&type1='+type1+'&type2='+type2+'&value1='+value1+'&value2='+value2+'&limit='+str(limit)
        )

# <---- USER METHODS ---->
class fm_user:
    """API user methods."""
    
    def __init__(self, api):
        self._request = api.request
    
    def getRecentTracks(self, user, limit=5):
        """Get recent tracks for a user."""
        data = self._request('method=user.getrecenttracks&user='+user+'&limit='+str(limit))
        if not 'recenttracks' in data or not 'track' in data['recenttracks']:
            return {'error':'foo', 'message':'No recent tracks.'}
        return data
