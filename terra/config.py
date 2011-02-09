''' terra.config
    Created by photofroggy
    
    Manages the configuration for Terra.
'''

# stdlib
import os
import sys
import json
# terra's stdlib
from terra.misc_lib import get_input
from terra.misc_lib import export_struct

class Settings:
    
    class info:
        def __init__(self):
            self.username = None
            self.password = None
            self.owner = None
            self.trigger = None
    
    autojoin = None
    token = None
    cookie = None
    file = None
    
    def __init__(self, file='./storage/config.bsv'):
        self.file = file
        self.info = Settings.info()
        self.autojoin = []
        self.load()
    
    def load(self):
        if not os.path.exists(self.file):
            return
        file = open(self.file, 'r')
        data = json.loads(file.read())
        file.close()
        self.info.username = data['info']['username']
        self.info.password = data['info']['password']
        self.info.owner = data['info']['owner']
        self.info.trigger = data['info']['trigger']
        self.autojoin = data['autojoin']
        self.token = data['token']
        self.cookie = data['cookie']
    
    def save(self):
        data = {
            'info': {
                'username': self.info.username,
                'password': self.info.password,
                'owner': self.info.owner,
                'trigger': self.info.trigger
            },
            'autojoin': self.autojoin,
            'token': self.token,
            'cookie': self.cookie
        }
        file = open(self.file, 'w')
        file.write(export_struct(data))
        file.close()

class Configure:
    
    file = './storage/config.bsv'
    
    def __init__(self, file='./storage/config.bsv', option=None):
        self.file = file
        if not os.path.exists('./storage'):
            os.mkdir('./storage', 0o755)
        self.write('Welcome to the configuration file!')
    
        self.data = Settings(self.file)
        
        if option == 'all' or not self.data.info.username:
            self.run_all()
        else:
            self.menu()
    
    def write(self, msg):
        sys.stdout.write('>>> {0}\n'.format(msg))
        sys.stdout.flush()
    
    def menu(self):
        while True:
            self.data.load()
            self.write('Current configuration:')
            # Display config data!
            info = self.data.info
            self.write('Bot {0} = {1}'.format('username', info.username))
            self.write('Bot {0} = {1}'.format('password', info.password))
            self.write('Bot {0} = {1}'.format('owner', info.owner))
            self.write('Bot {0} = {1}'.format('trigger', info.trigger))
            self.write('Autojoin:')
            self.write(', '.join(self.data.autojoin))
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
            setattr(self.data.info, option, get_input('> Bot ' + option + ': '))
    
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
                self.data.autojoin = [ns.strip() for ns in aj if ns.strip()]
        
        if not self.data.autojoin:
            self.data.autojoin.append('#Botdom')
    
    def save(self):
        self.data.save()
        
        self.write( 'Configuration file saved!' )
    
# EOF
