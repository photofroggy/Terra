''' Main Menu
    Created by photofroggy
    
    This is meant to be a simple little thing which
    acts as the main menu for the bot. The main menu
    does not always come up, as there are ways to run
    specific menu options instantly, but the menu does
    always get called first and foremost.
'''

import os
import sys
import subprocess
from terra.custom import get_input

def run(args, restartable=True):
    args = args[2:].lower()
    if not args in ('bot', 'debug', 'config', 'exit') or args == 'menu':
        restartable = False
        sys.stdout.write('===========> Main Menu <============\n>>> Welcome!\n>>> Please select an option!\n')
        sys.stdout.write('>> Bot - Run the bot.\n')
        sys.stdout.write('>> Debug - Run the bot in debug mode.\n')
        sys.stdout.write('>> Config - Configure the bot.\n')
        sys.stdout.write('>> Exit - Close this program.\n')
        sys.stdout.flush()
        while not args in ('bot', 'debug', 'config', 'exit'):
            args = get_input().lower()
    if args in ('bot', 'debug'):
        from terra import core
        ret = core.Main(args == 'debug', restartable)
        sys.stdout.write(('='*80))
        if ret.close and not (ret.restart and restartable):
            return
        argv = [(str(i) if not k else i) for k, i in enumerate(sys.argv)]
        if ret.restart and restartable:
            subprocess.Popen([sys.executable] + argv)
            return
        resp = ''
        while not resp in ('y', 'n'):
            resp = get_input('>> Would you like to reboot?[Y|N]: ').lower()
        if resp == 'y':
            sys.stdout.write(('='*80))
            subprocess.Popen([sys.executable] + argv)
            return
        input('>> Press enter to continue...')
        return
    if args == 'config':
        from terra.config import Configure
        Configure()
        if restartable:
            return
    if args == 'exit':
        return
    run('--menu', False)
    
# EOF
