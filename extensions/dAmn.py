
import time
from terra import extension
from rules.command import Event

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
        self.bind(self.c_say, 'command', ['say', 'Owner'])
        
        self.bind(self.c_ping, 'command', ['ping', 'Operators'], 'This shows the speed of the connection.')
    
    def c_say(self, cmd, dAmn):
        dAmn.say(cmd.target, cmd.arguments(1, True))
    
    def c_ping(self, cmd, dAmn):
        pingmsg = cmd.user + ': Ping?'
        self.bind(self.e_ping, 'recv_msg', [str(cmd.ns), dAmn.user.username, pingmsg])
        self.ping_msg.append(pingmsg)
        self.ping_usr.append(cmd.user)
        dAmn.say(cmd.ns, pingmsg)
        self.ping_ts.append(time.time())
    
    def e_ping(self, e, dAmn):
        if not e.message in self.ping_msg:
            return
        id = self.ping_msg.index(e.message)
        self.unbind(self.e_ping, 'recv_msg', [e.ns, e.user, e.message])
        dAmn.say(e.ns, '{0}: Pong! ({1})'.format( self.ping_usr.pop(id), str(time.time() - self.ping_ts.pop(id))[0:7] ))
        self.ping_msg.pop(id)
        
    
# EOF
