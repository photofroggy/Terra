
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
    
    def c_say(self, cmd, dAmn):
        dAmn.say(cmd.target, cmd.arguments(1, True))
        
    
# EOF
