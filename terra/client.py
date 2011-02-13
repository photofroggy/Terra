''' terra.client module
    Created by photofroggy
    
    This acts as the actual client component
    for Terra. It uses dAmn Viper and Reflex
    to work.
'''

# stdlib
import os
import sys
import time
from functools import wraps
# Lib imports!
from dAmnViper.base import ReconnectingClient
from reflex.data import Event
# terra lib
from terra.config import Settings

class Bot(ReconnectingClient):
    
    _config_file = None
    _events = None
    
    def __inst__(self, file, debug=False):
        super(Bot, self).__inst__()
        self._config_file = file
        self.flag.debug = debug
        self.flag.logging = True
        self.mute_channels = []
        self.load_config()
        self.user.password = None
    
    def set_evt_mgr(self, mgr):
        self._events = mgr
    
    def load_config(self):
        config = Settings(self._config_file)
        self.user.username = config.info.username
        self.user.password = config.info.password
        self.user.token = config.token
        self.owner = config.info.owner
        self.trigger = config.info.trigger
        self.autojoin = config.autojoin
    
    def save_config(self):
        config = Settings(self._config_file)
        config.info.trigger = self.trigger
        config.token = self.user.token
        config.cookie = self.user.cookie
        config.autojoin = self.autojoin
        config.save()
    
    def on_get_token(self):
        self.load_config()
    
    def on_token(self):
        self.user.password = None
        if self.session.status[0] != 1:
            return
        self.save_config()
    
    def pkt_generic(self, data):
        self._events.trigger(Event(data['event'], data['rules']), self)
    
    def say(self, ns, msg):
        if self.deform_ns(ns).lower() in self.mute_channels:
            return
        super(Bot, self).say(ns, msg)
    
    def mute_channel(self, ns):
        ns = self.deform_ns(ns).lower()
        if ns in self.mute_channels:
            return
        self.mute_channels.append(ns)
    
    def unmute_channel(self, ns):
        ns = self.deform_ns(ns).lower()
        if ns in self.mute_channels:
            return
        self.mute_channels.remove(ns)
    
    def logger(self, ns, msg, showns=True, mute=False, pkt=None):
        if self.flag.logging:
            self.save_msg(msg, ns)
        if not showns and ns != '~Global' and self.format_ns(ns) in self.channel.keys():
            if msg.startswith('** Got'):
                if self.channel[self.format_ns(ns)].member == {}:
                    return
        self.pnt_message(ns, '{0} {1}'.format(('{0}|'.format(ns) if showns else ''), msg), mute)
        
    def pnt_message(self, ns, message, mute=False):
        try:
            if (mute or ns.lower() in self.mute_channels) and not self.flag.debug:
                return
            sys.stdout.write('{0}{1}\n'.format(self.clock(), message))
            if self.flag.debug:
                self.save_msg(message, '~Debug')
        except UnicodeError:
            sys.stdout.write('{0} >> Received an unprintable message!\n'.format(self.clock()))
        sys.stdout.flush()
        
    def clock(self):
        return '{0}|'.format(time.strftime('%H:%M:%S'))
        
    def save_msg(self, msg, ns):
        if not os.path.exists('./storage'): os.mkdir('./storage', 0o755)
        if not os.path.exists('./storage/logs'): os.mkdir('./storage/logs', 0o755)
        if not os.path.exists('./storage/logs/' + ns): os.mkdir('./storage/logs/' + ns, 0o755)
        file = open('./storage/logs/{0}/{1}.txt'.format(ns, self._received), 'a')
        try:
            file.write('{0} {1}{2}'.format(self.clock(), msg.lstrip(), "\n"))
        except UnicodeEncodeError:
            file.write('{0} >> Unprintable message received in {1}!\n'.format(self.clock(), ns))
        file.close()
        
    def new_logger(self, ns='~Global', showns=True, mute=False):
        @wraps(self.logger)
        def wrapper(msg):
            return self.logger(ns, msg, showns, mute)
        return wrapper
