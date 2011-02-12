''' Commands Ruleset.
    This class controls event interactions for the event called "command".
'''

#stdlib
from functools import wraps
# Reflex
from reflex import data
from reflex import interfaces
# Viper
from dAmnViper.data import Channel
#lolol
from terra.misc_lib import arguments

class Ruleset(interfaces.Ruleset):

    def init(self, core, manager):
        self.index = {}
        self.core = core
        self.user = core.user
        self.username = core.config.info.username
        
    def bind(self, ext, meth, event, options, *additional):
        if not options: return None
        if not options[0]: return None
        if type(options[0]) in (type(()), type([])):
            if not options[0][0]: return None
        if 'command' in self.mapref:
            for binding in self.mapref['command']:
                if (binding.source, binding.call, binding.options) is (ext, meth, options):
                    return None
                if isinstance(options[0], str):
                    if options[0].lower() in self.index:
                        self._write( '>> Extension {0} tried to re-bind command {1}.'.format( ext, str(options[0]) ) )
                        return None
                else:
                    for name in options[0]:
                        if name.lower() in self.index:
                            self._write( '>> Extension {0} tried to re-bind command {1}.'.format( ext, str(name) ) )
                            return None
        else: self.mapref['command'] = []
        new_cmd = Binding(ext, meth, 'command', [(i if not isinstance(i, Channel) else str(i)) for i in options], additional)
        new_cmd.set_privs(self.user.groups)
        self.mapref['command'].append(new_cmd)
        key = len(self.mapref['command'])-1
        if isinstance(options[0], str):
            self.index[options[0].lower()] = key
        else:
            for ns in options[0]:
                self.index[ns.lower()] = key
        return new_cmd
    
    def unbind(self, ext, method, event, options=None):
        if not options:
            return
        if isinstance(options[0], str):
            cmd = options[0].lower()
        else:
            for cmd in options[0]:
                newopt = options
                newopt[0] = cmd.lower()
                self.unbind(ext, method, newopt)
            return
        if 'command' in self.mapref.keys():
            if not cmd in self.index.keys():
                return
            if not self.mapref['command'][self.index[cmd]].source.lower() == ext.lower():
                return
            del self.mapref['command'][self.index[cmd]]
        if len(self.mapref['command']) == 0:
            del self.mapref['command']
        self.sort_index()
    
    def trigger(self, data, rules, dAmn):
        """Trigger a command."""
        if not data.trigger.lower() in self.index.keys():
            return [False]
        return [self.run(self.mapref['command'][self.index[data.trigger.lower()]], data, rules, dAmn)]
            
    def run(self, binding, data, rules, dAmn):
        """Attempt to run a command's event binding."""
        for i, option in enumerate(binding.options):
            if not option: continue
            if i is 0: continue
            if i is 1:
                if not self.privd(data.user, binding.level, data.trigger):
                    return None
                continue
            if i is 2:
                if dAmn.format_ns(str(option)).lower() == str(data.ns).lower():
                    continue
                return None
            rule = rules[i]
            if isinstance(rule, str):
                if str(rule).lower() == option.lower():
                    continue
            if rule is option:
                continue
            return None
        if data.arguments(1) == '?':
            if binding.additional and binding.additional[0]:
                dAmn.say(data.target, ': '.join([str(data.user), binding.additional[0]]))
                return None
            dAmn.say(data.target, data.user+': There is no information for this command.')
            return None
        if self.debug:
            self._write('** Running command \''+data.trigger+'\' for '+str(data.user)+'.')
        try:
            binding.call(data, dAmn)
        except Exception as e:
            log = dAmn.new_logger(showns = False)
            log('>> Failed to execute command "{0}"!'.format(data.trigger))
            log('>> Error message: {0}.'.format(e.args[0]))
        return None
    
    def reloading(self):
        self.index = {}
    
    def privd(self, user, level, cmd):
        """Check if users_group inherits access to group. User and cmd are provided in the event of errors."""
        if self.user.has(user) >= level:
            return True
        self._write('>> User ' + str(user) + ' was denied access to the command \'' + cmd + '\'.')
        return False
    
    def sort_index(self):
        temp = self.index
        self.index = {}
        for name in temp:
            for key, binding in enumerate(self.mapref['command']):
                if isinstance(binding.options[0], str):
                    if name != binding.options[0].lower():
                        continue
                    self.index[name] = key
                    continue
                if name in [ns.lower() for ns in binding.options[0]]:
                    self.index[name] = key

class Event(data.Event):
    """Command event class."""
    
    def __inst__(self, event, data):
        self.arguments = self._args_wrapper(self.message)
        
    def __str__(self):
        return '<event[\'command:'+self.trigger+'\']>'
    
    def _args_wrapper(self, message):
        @wraps(arguments)
        def wrapper(start=0, finish=False, separator=' ', sequence=False):
            return arguments(message, start, finish, separator, sequence)
        return wrapper

class Binding(data.Binding):
    """Command Binding class."""
        
    def __inst__(self):
        cmd = self.options[0] if isinstance(self.options[0], str) else self.options[0][0]
        self.type = '<event[\'command:'+cmd+'\'].binding>'
    
    def set_privs(self, groups):
        grp = 'Guests'
        if len(self.options) > 1:
            grp = self.options[1] if self.options[1] != None else 'Guests'
            if grp != 'Guests':
                grp = groups.find(grp, True)
                if grp is None: grp = 'Guests'
        self.group = grp
        self.level = groups.find(grp)

# EOF
