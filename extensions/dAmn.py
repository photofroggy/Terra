
import time
from reflex.data import Event
from terra import extension

class Extension(extension.API):

    about = 'This is the extension grouping all dAmn-related commands.'    
    version = 1
    # Yep, I made this one.
    author = 'photofroggy'
    
    whois_usr = []
    whois_ns = []
    whois_fr = []
    
    ping_msg = []
    ping_usr = []
    ping_ts = []
    
    def init(self):
        # Configure our dAmn Commands!!
        self.bind(self.e_recv_msg, 'recv_msg')
    
    def e_recv_msg(self, event, dAmn):
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
            if not None in self.trigger(
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
        
    
# EOF
