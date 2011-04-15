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
from reflex.data import Event
from dAmnViper.base import ReconnectingClient
# terra lib
from terra.config import Settings
from terra.console import Logger

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
        self.console = Logger(self, self.flag.logging, debug)
    
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
    
    def pkt_login(self, data):
        self.console.start()
        super(Bot, self).pkt_login(data)
    
    def pkt_disconnect(self, data):
        self.console.stop()
        super(Bot, self).pkt_disconnect(data)
        while self.console.running:
            time.sleep(.4)
    
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
        self.console.write(time.time(), ns, msg, showns, mute, pkt)
        
    def new_logger(self, ns='~Global', showns=True, mute=False):
        @wraps(self.logger)
        def wrapper(msg):
            return self.logger(ns, msg, showns, mute)
        return wrapper
