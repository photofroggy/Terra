''' terra.core
    Created by photofroggy
    
    The main module for the bot.
    The Main class ties everything together!
'''

# stdlib
import os
import sys
import time
# custom libs
from reflex.data import Event
from reflex.control import EventManager
# terra libs
from terra import extension
from terra.client import Bot
from terra.config import Settings
from terra.config import Configure

class Main:
    
    class info:
        name = 'Terra'
        version = 2
        state = 'alpha'
        series = 'Legacy'
        build = 118
        stamp = '10022011-012452'
        rstamp = 0.0
        author = 'photofroggy'
    
    start = 0.0
    config = False
    
    config_file = './storage/config.bsv'
    close = True
    restart = False
    exit_msgs = ['** The bot has finished running.',
            '** Bye bye!' ]
    
    def __init__(self, debug=False, restartable=True):
        self.start = time.time()
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
        self.exts = extension.Manager(self.log, self.debug)
    
    def intro(self):
        inf = self.info
        self.log('** Hello thar!')
        self.log('** Welcome to {0} {1} {2} by {3}.'.format(inf.name, inf.version, inf.state, inf.author))
        self.log('** Build {0} ({1}) {2}.'.format(inf.build, inf.stamp, inf.series))
        self.log('** Released under GNU GPL v3.')
    
    def config(self):
        conf = Settings(self.config_file)
        if conf.info.username is None:
            self.log('** Looks like you need to set up the bot!')
            self.log('** Loading config file...')
            Configure(self.config_file, 'all')
        conf.load()
        conf.info.password = None
        conf.save = lambda n=None: n
        self.config = conf
    
    def load_rules(self):
        self.log('** ... load rules here.')
    
    def load_exts(self):
        self.exts.load_extensions(self, self.evts)
    
    def run(self):
        self.log('** Ok, that\'s everything! Let\'s go!')
        self.conn.start()
        for msg in self.exit_msgs:
            self.log(msg)
        
