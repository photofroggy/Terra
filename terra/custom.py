''' terra.Custom - part of Terra.
    Copyright (C) 2009  Henry Rapley
    Released under GNU GPL v3.
'''

import os
import sys
import time
import json
from functools import wraps
from terra.rules import command
from terra.misc_lib import export_struct
from terra.misc_lib import clean_files
from terra.misc_lib import create_folders
    
def get_input(prefix='> ', empty=False):
    while True:
        ins = input(prefix)
        if (len(ins) == 0 and empty) or len(ins) > 0:
            return ins

class config:
    
    file = './storage/config.bsv'
    
    def __init__(self, option=None):
        if not os.path.exists('./storage'):
            os.mkdir('./storage', 0o755)
        self.write('Welcome to the configuration file!')
        sys.stdout.flush()
    
        self.data = {
            'info': {},
            'autojoin':[],
            'authtoken':''
        }
        
        if option == 'all' or not os.path.exists(self.file):
            self.run_all()
        else:
            self.menu()
    
    def write(self, msg):
        sys.stdout.write('>>> {0}\n'.format(msg))
        sys.stdout.flush()
    
    def menu(self):
        while True:
            file = open(self.file, 'r')
            self.data = json.loads(file.read())
            file.close()
            self.write('Current configuration:')
            for key, value in self.data['info']:
                self.write('Bot {0} = {1}'.format(key, value))
            self.write('Autojoin:')
            self.write(', '.join(self.data['autojoin']))
            self.write('')
            self.write('Choose one of the following options:')
            self.write('info - Set the bot\'s configuration information.')
            self.write('autojoin - Set the bot\'s autojoin list.')
            self.write('all - Set all configuration data.')
            self.write('exit - Leave the configuration file.')
            ins = ''
            while not ins in ('all', 'autojoin', 'exit', 'info'):
                ins = get_input('>> ').lower()
            if ins == 'exit':
                return
            if ins == 'all':
                self.run_all()
                continue
            if ins == 'info':
                self.get_info()
                self.save()
                continue
            if ins == 'autojoin':
                self.get_autojoin()
                self.save()
    
    def run_all(self):
        self.write('Please fill in the following appropriately.')
        self.get_info()
        self.get_autojoin()
        self.write('Ok! That was everything we needed!')
        self.save()
    
    def get_info(self):
        for option in ['username', 'password', 'owner', 'trigger']:
            self.data['info'][option] = get_input('> Bot ' + option + ': ')
    
    def get_autojoin(self):
        self.write( 'Next we need to know which channels you want your' )
        self.write( 'bot to join on startup. Please enter a list of' )
        self.write( 'channels below, separated by commas. Each channel' )
        self.write( 'must begin with a hash (#) or chat:. Leave blank' )
        self.write( 'to use the default (#Botdom).' )
    
        aj = get_input('> ', True)
        if aj:
            aj = aj.split(',')
            if aj:
                self.data['autojoin'] = [ns.strip() for ns in aj if ns.strip()]
        
        if not self.data['autojoin']:
            self.data['autojoin'].append('#Botdom')
    
    def save(self):
        file = open(self.file, 'w')
        file.write(export_struct(self.data))
        file.close()
        
        self.write( 'Configuration file saved!' )
    
# EOF
