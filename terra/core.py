''' terra.core
    Created by photofroggy
    
    The main module for the bot.
    The Main class ties everything together!
'''

# stdlib
import os
import sys
import time
import platform
# custom libs
from reflex.data import Event
from reflex.control import EventManager
# terra libs
from terra import users
from terra import ruleset
from terra import extension
from terra.client import Bot
from terra.config import Settings
from terra.config import Configure
from terra.misc_lib import clean_files

class Main:
    
    class info:
        name = 'Terra'
        version = 2
        state = 'Development'
        series = 'Legacy'
        build = 120
        stamp = '20022011-010913'
        rstamp = 1298164153.7
        author = 'photofroggy'
    
    start = 0.0
    config = None
    
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
        self.configure()
        self.conn.agent = self.agent(self.conn.platform, self.info)
        self.load_users()
        self.load_rules()
        self.load_exts()
        self.evts.trigger(Event('ready'), self.conn)
        self.run()
    
    def load_core(self):
        """ Load the core components for the bot. """
        # Load our dAmn client!
        self.conn = Bot(self.config_file, self.debug)
        # Store a logger so we can more easily write messages.
        self.log = self.conn.new_logger(showns=False)
        self.dlog = self.conn.new_logger('~Global', False, True)
        # Load an event manager.
        self.evts = EventManager(output=self.log, debug=self.debug)
        # Give our dAmn client a reference to the event manager.
        self.conn.set_evt_mgr(self.evts)
        # Load a config object.
        self.config = Settings(self.config_file)
        # Load some more managers.
        self.exts = extension.Manager(self, self.debug)
        self.rules = ruleset.Manager(self, self.debug)
        self.user = users.Manager(self, './storage/users.bsv', self.debug)
    
    def intro(self):
        inf = self.info
        self.log('** Hello thar!')
        self.log('** Welcome to {0} {1} {2} by {3}.'.format(inf.name, inf.version, inf.state, inf.author))
        self.log('** Build {0} ({1}) {2}.'.format(inf.build, inf.stamp, inf.series))
        self.log('** Released under GNU GPL v3.')
    
    def configure(self):
        self.config.load()
        if self.config.info.username is None:
            self.log('** Looks like you need to set up the bot!')
            self.log('** Loading config file...')
            Configure(self.config_file, 'all')
            self.config.load()
            self.conn.load_config()
        self.config.info.password = None
        self.config.save = lambda n=None: n
    
    def load_rules(self):
        self.rules.load_rules(self, self.evts)
    
    def load_exts(self):
        self.exts.load_extensions(self, self.evts)
    
    def load_users(self):
        self.user.load(self.config.info.owner)
    
    def agent(self, inf, mnplat):
        uname = platform.uname()
        name, release, version = uname[:3]
        return ''.join(['Python/{0}.{1} '.format( str(os.sys.version_info[0]), str(os.sys.version_info[1]) ),
            '({0}; U; {1} {2}; en-GB; {3}) '.format(name, release, version, self.config.info.owner),
            '/'.join([mnplat.name, mnplat.stamp.replace('-','')]),
            ' {0}/{1}.{2}'.format(inf.name, str(inf.version), str(inf.build))
        ])
    
    def run(self):
        clean_files()
        self.conn.start()
        for msg in self.exit_msgs:
            self.log(msg)
        self.close = self.conn.flag.close
        self.restart = self.conn.flag.restart
