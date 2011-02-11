
import time
import os
import platform
from hashlib import md5
from terra import extension

class Extension(extension.API):
    
    about = 'These are the system commands. Use them to manage your bot as a whole.'
    version = 1
    author = 'photofroggy'
        
    def init(self):
        # COMMANDS
        # Info commands.
        self.bind(self.c_about, 'command', ['about'], 'View some brief information about this bot!')
        
        self.bind(self.c_quit, 'command', ['quit', 'Owner'], 'Turn off the bot with this command.')
        
        self.bind(self.e_recv_msg, 'recv_msg')
        
        bname = self.cconfig.info.username.lower()
        # Trigcheck strings..
        self.tcs = [
            bname + ': trigcheck',
            bname + ': trigger',
            bname + ', trigcheck',
            bname + ', trigger'
        ]
    
    def c_about(self, cmd, dAmn):
        """This command displays some brief information about the bot."""
        dAmn.say(
            cmd.ns,
            '<abbr title="{0}"></abbr>{1}<br/><sub><b>Author:</b> :dev{2}:<b>; Owner:</b> :dev{3}:<b>;</b>{4}</sub>'.format(
                cmd.user,
                '<b>{0} {1} {2}</b> ({3})'.format(
                    self.core.info.name, self.core.info.version, self.core.info.state, self.core.info.series),
                self.core.info.author,
                dAmn.owner,
                '' if not dAmn.flag.debug else '<br/><i>Currently running in debug mode.</i>'
            )
        )
        
    def c_quit(self, cmd, dAmn):
        """Shut down or restart the bot."""
        restarting = False
        dAmn.say(
            cmd.ns,
            '{0}: {1}.'.format(
                cmd.user,
                'Restarting' if restarting else 'Quitting'
            )
        )
        self.core.exit_msgs[0] = '** Bot {1} on request by {0}.'.format(
            cmd.user,
            'restarting' if restarting else 'shutting down'
        )
        dAmn.flag.quitting = True
        dAmn.flag.disconnecting = True
        dAmn.flag.restart = restarting
        dAmn.disconnect()
    
    def e_recv_msg(self, Evt, dAmn):
        """ Check for trigcheck and botcheck. """
        if not self.user.has(Evt.user, 'guests'):
            return
        # Trigcheck
        if Evt.message.lower() in self.tcs:
            dAmn.say(
                Evt.ns,
                '{0}: My trigger is <code>{1}</code>'.format(
                    Evt.user,
                    dAmn.trigger.replace('&', '&amp;')
                )
            )

# EOF
