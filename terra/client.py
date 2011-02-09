''' terra.client module
    Created by photofroggy
    
    This acts as the actual client component
    for Terra. It uses dAmn Viper and Reflex
    to work.
'''

# Lib imports!
from dAmnViper.base import ReconnectingClient
from reflex.data import Event
# terra lib
from terra.config import Settings

class Bot(ReconnectingClient):
    
    _config_file = None
    _events = None
    
    def __inst__(self, events, file):
        super(Bot, self).__inst__()
        self._config_file = file
        self._events = events
        self.load_config()
        self.user.password = None
    
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
        if not self.session.status[0] != 1:
            return
        self.save_config()
    
    def pkt_generic(self, data):
        self._event.trigger(Event(data['event'], data['rules']), self)
