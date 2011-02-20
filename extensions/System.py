
import os
import time
import platform
from hashlib import md5
from terra import extension
from terra import misc_lib

class Extension(extension.API):
    
    about = 'These are the system commands. Use them to manage your bot as a whole.'
    version = 1
    author = 'photofroggy'
        
    def init(self):
        # COMMANDS
        # Info commands.
        self.bind(self.c_about, 'command', ['about'], 'View some brief information about this bot!')
        self.bind(self.c_build, 'command', ['build'], 'View the build information for this bot!')
        self.bind(self.c_system, 'command', ['system'], 'View information about the system.')
        self.bind(self.c_uptime, 'command', ['uptime'], 'See how long the bot has been running for.')
        self.bind(self.c_commands, 'command', ['commands'], 'List the bot\'s commands!')
        self.bind(self.c_quit, 'command', [['quit', 'restart'], 'Owner'], 'Turn off the bot with this command.')
        
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
    
    def c_build(self, cmd, dAmn):
        """View this bot's build information."""
        dAmn.say(
            cmd.target,
            '{0}: Current build: Build {1} ({2}) {3}'.format(
                cmd.user, self.core.info.build,
                self.core.info.stamp, self.core.info.series
            )
        )
    
    def c_system(self, cmd, dAmn):
        """View system information for the bot."""
        inf = dAmn.platform
        rplat = self.core.evts.info
        msg = ['<abbr title="' + cmd.user + '"></abbr><b>System information:</b><sub>']
        msg.append('<b> - Platform:</b> ' + ' '.join([platform.platform(1,1), platform.version()]))
        msg.append('<b> - Runtime Environment:</b> <code>Python ' + os.sys.version.replace("\n", '') + '</code>')
        msg.append(
            '<b> - dAmn engine:</b> ' + ' '.join(
                [
                    inf.name, str(inf.version), inf.state,
                    '- Build ' + str(inf.build) + ' (' + str(inf.stamp) + ') ' + inf.series
                ]
            )
        )
        msg.append(
            '<b> - Event engine:</b> '+ ' '.join(
                [
                    'Reflex', str(rplat.version), rplat.state,
                    '- Build', str(rplat.build), '('+str(rplat.stamp)+')', rplat.name
                ]
            )
        )
        msg.append(
            '<b> - Core:</b> ' + ' '.join(
                [
                    self.core.info.name, str(self.core.info.version), self.core.info.state,
                    '- Build', str(self.core.info.build), '(' + str(self.core.info.stamp) + ')', self.core.info.series
                ]
            )
        )
        msg.append('<b> - Uptime:</b> ' + self.getuptime())
        dAmn.say(cmd.target, '<br/>'.join(msg))
    
    def c_uptime(self, cmd, dAmn):
        """View how long the bot has been running for."""
        dAmn.say(cmd.target, '<abbr title="{0}"></abbr>Uptime: {1}.'.format(cmd.user, self.getuptime()))
    
    def c_commands(self, cmd, dAmn):
        dAmn.say(cmd.target, self.full_cmd_list(cmd.user))
    
    def full_cmd_list(self, user):
        grps = self.user.groups.get()
        cmds = []
        cmdn = 0
        for group in grps:
            names = [x.lower() for x in group if x is not None]
            gcmds = []
            for binding in self.core.evts.map['command']:
                if binding.group.lower() in names:
                    cmdn+= 1
                    if type(binding.options[0]) in (type(()), type([])):
                        cmdn+= len(binding.options[0])-1
                        cmdname = ', '.join(binding.options[0])
                    else:
                        cmdname = binding.options[0]
                    gcmds.append(
                        '<abbr title="Extension: {0}; Method: {1};">{2}</abbr>'.format(
                            binding.source, binding.call.__name__, cmdname))
            if len(gcmds) == 0:
                continue
            cmds.insert(0, '- <b> <abbr title="real: {0}">{1}</abbr>:</b> {2}'.format(
                group[0], group[1] or group[0], ', '.join(gcmds)))
        return '<abbr title="{0}"></abbr><b>{1} available commands:</b><br/><sub>{2}</sub>'.format(
            user, cmdn, '<br/>'.join(cmds))
        
    def c_quit(self, cmd, dAmn):
        """Shut down or restart the bot."""
        restarting = cmd.trigger.lower() == 'restart'
        if restarting and not self.core.restartable:
            dAmn.say(cmd.ns, cmd.user + ': Terra cannot be restarted when run from the menu.')
            return
        dAmn.say(
            cmd.ns,
            '{0}: {1} after running for {2}.'.format(
                cmd.user,
                'Restarting' if restarting else 'Quitting',
                self.getuptime()
            )
        )
        self.core.exit_msgs[0] = '** Bot {1} on request by {0}.'.format(
            cmd.user,
            'restarting' if restarting else 'shutting down'
        )
        dAmn.flag.quitting = True
        dAmn.flag.disconnecting = True
        dAmn.flag.restart = restarting
        dAmn.flag.close = cmd.arguments(1).lower() != 'soft'
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
    
    def getuptime(self):
        return misc_lib.strftimelen(time.time() - self.core.start)

# EOF
