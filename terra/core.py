''' terra.core
    Created by photofroggy
    
    The main module for the bot.
    The Main class ties everything together!
'''

# stdlib
import os
import sys
# custom libs
from reflex.data import Event
from reflex.control import EventManager
# terra libs
from terra.client import Bot
from terra.config import Settings
from terra.config import Configure

class Main:
    
    class vinfo:
        version = 2
        state = 'pre-alpha'
        build = 118
        stamp = '00000000-000000'
        rstamp = 0.0
        author = 'photofroggy'
    
    config_file = './storage/config.bsv'
    close = True
    restart = False
    exit_msgs = ['** The bot has finished running.',
            '** Bye bye!' ]
    
    def __init__(self, debug=False, restartable=True):
        self.debug = debug
        self.restartable = restartable
        self.load_core()
        self.intro()
        self.config()
        self.load_rules()
        self.load_exts()
        self.run()
    
    def load_core(self):
        self.conn = Bot(self.config_file, self.debug)
        self.log = self.conn.new_logger(showns=False)
        self.evts = EventManager(output=self.log)
        self.conn.set_evt_mgr(self.evts)
    
    def intro(self):
        self.log('** Welcome to Terra version 2!')
        self.log('** Created by photofroggy!')
    
    def config(self):
        conf = Settings(self.config_file)
        if conf.info.username is not None:
            return
        self.log('** Looks like you need to set up the bot!')
        self.log('** Loading config file...')
        Configure(self.config_file)
    
    def load_rules(self):
        self.log('** ... load rules here.')
    
    def load_exts(self):
        self.log('** ... load extensions here.')
    
    def run(self):
        self.log('** Ok, that\'s everything! Let\'s go!')
        self.conn.start()
        for msg in self.exit_msgs:
            self.log(msg)
        
