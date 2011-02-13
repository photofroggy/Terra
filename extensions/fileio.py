''' FileIO by photofroggy.
    Example of how to use Terra's extension
    API to read and write data from files
    on the computer.
'''

from terra import extension
from terra.misc_lib import export_struct

class Extension(extension.API):
    
    # Configure the extension!
    about = 'Example file IO operations.'
    version = 1
    author = 'photofroggy'
    
    def init(self):
        # Attribute storing data from the flattext file.
        self.flattext = ''
        # Attribute storing data from the JSON file.
        self.jsonf = None
        # Attribute storing data from the pickle file.
        self.picklef = None
        # Binding events
        self.bind(self.c_load, 'command', ['loadf', 'Owner'])
        self.bind(self.c_save, 'command', ['savef', 'Owner'])
        self.bind(self.c_read, 'command', ['readf', 'Owner'])
        # Create our storage object.
        self.locker()
        # Load data from files.
        self.load()
        
    def c_load(self, cmd, dAmn):
        dAmn.say(cmd.ns, cmd.user+': Loading data from files.')
        self.load()
        
    def c_save(self, cmd, dAmn):
        sub_command = cmd.arguments(1).lower()
        if not sub_command in ('flat', 'json'):
            dAmn.say(cmd.ns, cmd.user+': Choose whether to save data in the <b>flat</b> or <b>json</b> file.')
            return
        data = cmd.arguments(2, True)
        if not data:
            dAmn.say(cmd.ns, cmd.user+': You must set the data to save in the file.')
            return
        if sub_command == 'flat':
            self.flattext = data
        if sub_command == 'json':
            self.jsonf = {'channel': cmd.ns, 'message': data}
        self.save()
        dAmn.say(cmd.ns, cmd.user+': Data saved!')
        
    def c_read(self, cmd, dAmn):
        sub_command = cmd.arguments(1).lower()
        if not sub_command in ('flat', 'json'):
            dAmn.say(cmd.ns, cmd.user+': Choose whether to read the data in the <b>flat</b> or json</b> file.')
            return
        data = None
        
        if sub_command == 'flat':
            data = self.flattext
        if sub_command == 'json':
            data = self.jsonf
            
        dAmn.say(cmd.ns, 'data in file:<br/><bcode>'+export_struct(data))
        
    def load(self):
        # Load the data from the flattext file.
        self.flattext = self.storage.read('flattext')
        if not self.flattext:
            self.flattext = ''
        # Load the data from the json file.
        self.jsonf = self.storage.loads('jsonf')
        if not self.jsonf:
            self.jsonf = None
        
    def save(self):
        self.storage.write('flattext', self.flattext)
        self.storage.dumps('jsonf', self.jsonf)
    
