''' terra.extension
    Created by photofroggy
    
    This provides a basic API for extensions, based on
    reflex reactors. The extension management is also
    provided by this module.
'''

# stdlib
import imp
import pkgutil
import traceback
# reflex lib
from reflex.interfaces import Reactor
# Extensions
import extensions

class API(Reactor):
    
    def __init__(self, core, manager, *args, **kwargs):
        self.core = core
        self.cconfig = core.config
        self.user = core.user
        self.log = core.log
        self.name = str(self.__class__).split('.')[1].replace('_', ' ')
        super(API, self).__init__(manager, *args, **kwargs)
    
class Manager:
    
    def __init__(self, core, debug=False):
        self.log = core.log
        self.dlog = core.dlog
        self.debug = debug
        self.modules = {}
        self.loaded = {}
    
    def load_modules(self):
        self.dlog('** Checking modules in extensions folder.')
        modules = {}
        walker = pkgutil.walk_packages(extensions.__path__, extensions.__name__ + '.')
        for tup in walker:
            name = tup[1]
            
            self.dlog('** Found module \'{0}\'.'.format(name))
                
            if name in self.modules.keys():
                self.dlog('** Previously loaded module. Reloading!')
                imp.reload(self.modules[name])
                modules[name] = self.modules[name]
                continue
                
            loader = pkgutil.find_loader(name)
            mod = loader.load_module(name)
            
            if not hasattr(mod, 'Extension'):
                self.dlog('>> Ignoring extension module {0}.'.format(name))
                self.dlog('>> Module contains no Extension class.')
                continue
            
            modules[name] = mod
        self.modules = modules
    
    def load_extensions(self, core, manager):
        self.log('** Loading extensions...')
        self.load_modules()
        self.loaded = {}
        for name, mod in self.modules.items():
            try:
                extobj = mod.Extension(core, manager)
                extname = extobj.name
                self.loaded[extname] = extobj
            except Exception as e:
                self.log('>> Failed to load extension from {0}!'.format(name))
                self.log('>> Error:')
                tb = traceback.format_exc().splitlines()
                for line in tb:
                    self.log('>> {0}'.format(line))
        
        self.dlog('** Loaded extensions: {0}'.format(', '.join(self.loaded.keys())))
