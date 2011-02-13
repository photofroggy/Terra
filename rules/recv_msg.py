''' rules.recv_msg
    Created by photofroggy
    
    This simply makes sure commands are always fired!
    No extension dependencies! Yay!
'''

# Reflex
from reflex import interfaces
from rules.command import Event

class Ruleset(interfaces.Ruleset):
    
    def init(self, core, manager):
        self.e_trigger = manager.trigger
        self.core = core
        self.ruleref = core.evts.rules
    
    def trigger(self, data, rules, dAmn):
        self.check_command(data, rules, dAmn)
        if not 'recv_msg' in self.mapref.keys():
            return [None]
        return [self.ruleref['default'].run(binding, data, rules, dAmn) for binding in self.mapref['recv_msg']]
            
    def check_command(self, event, rules, dAmn):
        if event.user.lower() == dAmn.user.username.lower():
            return
        if event.message[:len(dAmn.trigger)] == dAmn.trigger:
            message = event.message[len(dAmn.trigger):]
            splitmsg = message.split(' ')
            findns = '' if not len(splitmsg) > 1 else splitmsg[1]
            if findns[:1] in ('#', '@') and findns[1:] and not findns[1:2] in ('#', '@'):
                target = dAmn.format_ns(findns)
                splitmsg.pop(1)
                message = ' '.join(splitmsg)
                for cs in dAmn.channel.keys():
                    if cs.lower() == str(target).lower():
                        target = dAmn.channel[cs].namespace
            else:
                target = event.ns
            if not None in self.e_trigger(
                Event(
                    'command',
                    [('trigger', splitmsg[0]), ('user_group', ''),
                        ('ns', event.ns), ('user', event.user),
                        ('message', message), ('target', target), ('raw', event.raw)]
                ), dAmn
            ) and dAmn.flag.debug:
                dAmn.logger('~Global',
                    '>> {0} tried to execute non-existant command "{1}".'.format( str(event.user), splitmsg[0] ),
                    False)
