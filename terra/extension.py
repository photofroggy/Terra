''' terra.extension
    Created by photofroggy
    
    This provides a basic API for extensions, based on
    reflex reactors. The extension management is also
    provided by this module.
'''

# stdlib
import os
import imp
import json
import pkgutil
import traceback
from functools import wraps
# reflex lib
from reflex.interfaces import Reactor
# Extensions
import extensions
# lol terra lib
from terra.misc_lib import export_struct

class API(Reactor):
    
    name = None
    
    def __init__(self, core, manager, *args, **kwargs):
        self.core = core
        self.cconfig = core.config
        self.user = core.user
        self.log = core.log
        if self.name is None:
            self.name = str(self.__class__).split('.')[1].replace('_', ' ')
        super(API, self).__init__(manager, *args, **kwargs)
    
    def locker(self):
        self.storage = Storage(self.name)
    

class Storage:
    
    def __init__(self, name):
        self._dir = os.path.realpath(os.path.join('.', 'storage', 'ext', name))
        self.read = self.file_op(self._read)
        self.write = self.file_op(self._write)
        self.loads = self.file_op(self._loads)
        self.dumps = self.file_op(self._dumps)
        self.unlink = self.file_op(self._unlink)
    
    def file_op(self, method):
        """Pseudo-decorator for file operations."""
        @wraps(method)
        def new_file_op(file, *args, **kwargs):
            """Perform a file operation of some sort!"""
            file = (file+'.bsv').replace('../', '').replace('./', '').replace('..\\', '').replace('.\\', '')
            file = os.path.normpath(os.path.join(self._dir, file))
            if method.__name__ in ('_read', '_loads', '_unpickle') and not os.path.exists(file):
                self._closesavedir()
                return None
            self._loadsavedir()
            ret = method(file, *args, **kwargs)
            self._closesavedir()
            return ret
        return new_file_op
            
    def _read(self, file):
        """Read data from a file in your storage directory."""
        fp = open(file, 'r')
        data = fp.read()
        fp.close()
        return data
    
    def _write(self, file, data):
        """Write data to a file."""
        fp = open(file, 'w')
        data = fp.write(data)
        fp.close()

    def _loads(self, file):
        """Read JSON data from a file."""
        f = open(file, 'r')
        data = json.loads(f.read())
        f.close()
        return data
    
    def _dumps(self, file, data, pretty=True):
        """Write an object to a file as JSON."""
        f = open(file, 'w')
        f.write(json.dumps if not pretty else export_struct(data))
        f.close()
        
    def _unlink(self, file):
        """Delete a file."""
        try: os.unlink(file)
        except OSError:
            pass

    def _loadsavedir(self):
        """Create any needed directories."""
        if not os.path.exists(os.path.join('.', 'storage')):
            os.mkdir(os.path.join('.', 'storage'), 0o755)
        if not os.path.exists(os.path.join('.', 'storage', 'ext')):
            os.mkdir(os.path.join('.', 'storage', 'ext'), 0o755)
        if not os.path.exists(self._dir):
            os.mkdir(self._dir, 0o755)
    
    def _closesavedir(self):
        """Remove any empty folders."""
        if os.path.exists(self._dir):
            if not os.listdir(self._dir):
                try: os.rmdir(self._dir)
                except OSError: pass
        if os.path.exists(os.path.join('.', 'storage', 'ext')):
            if not os.listdir(os.path.join('.', 'storage', 'ext')):
                try: os.rmdir(os.path.join('.', 'storage', 'ext'))
                except OSError: pass

    
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
