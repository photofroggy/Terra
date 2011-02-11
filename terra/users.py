''' terra.users
    Created by photofroggy
    
    Manages user privileges for the bot.
'''

import os
import json
from terra.misc_lib import export_struct

class Manager:
    
    def __init__(self, core, file='./storage/users.bsv', debug=False):
        self.file = file
        self.owner = core.config.info.owner
        self.log = core.log
        self.debug = debug
        self.map = []
        self.groups = Groups()
    
    def load(self):
        self.log('** Loading user data...')
        if not os.path.exists(self.file):
            if self.debug:
                self.log('>> No user data found! Setting default user list!')
            self.map = self.defaults()
            self.load_groups()
            self.save()
        else:
            file = open(self.file, 'r')
            self.map = json.loads(file.read())
            file.close()
            self.load_groups()
        if self.debug:
            self.log('** User data loaded.')
    
    def save(self):
        if self.debug:
            self.log('** Saving user data...')
        self.save_groups()
        file = open(self.file, 'w')
        file.write(export_struct(self.map))
        file.close()
        if self.debug:
            self.log('** User data saved.')
    
    def load_groups(self):
        grps = [[grp[0], grp[1]] for grp in self.map]
        self.groups.set(grps)
    
    def save_groups(self):
        grps = self.groups.get()
        for i in range(0, len(grps)):
            self.map[i][0] = grps[i][0]
            self.map[i][1] = grps[i][1]
    
    def defaults(self):
        return [
            ['Banned', None, []],
            ['Guests', None, []],
            ['Members', None, []],
            ['Operators', None, []],
            ['Owner', None, [self.owner]],
        ]
    
    def find(self, user, name=False):
        for i, group in enumerate(self.map):
            for privd in group[2]:
                if privd.lower() == user.lower():
                    if name:
                        return group[1] or group[0]
                    return i
        return 1 if not name else self.groups.name(1)
    
    def has(self, user, group):
        priv = self.groups.find(group)
        user_priv = self.find(user)
        return user_priv >= priv
    

class Groups:
    
    def __init__(self):
        self.groups = []
    
    def set(self, seq):
        self.groups = seq
    
    def get(self):
        return self.groups
    
    def set_alias(self, group, alias=None):
        index = self.find(group)
        if index < 0:
            return False
        self.groups[index][1] = alias
        return True
    
    def find(self, group, name=False):
        group = group.lower()
        for i in range(0, len(self.groups)):
            names = [x.lower() for x in self.groups[i] if x is not None]
            if group in names:
                return i if not name else self.name(i)
        return -1 if not name else None
    
    def name(self, num):
        if num < 0 or num >= len(self.groups):
            return None
        return self.groups[num][1] or self.groups[num][0]

# EOF
