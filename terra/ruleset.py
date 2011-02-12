''' terra.ruleset
    Created by photofroggy
    
    Ruleset manager!
'''

# stdlib
import imp
import pkgutil
# reflex lib
from reflex.interfaces import Reactor
# Rulesets
import rules
    
class Manager:
    
    def __init__(self, writer, debug=False):
        self.log = writer
        self.debug = debug
        self.modules = {}
        self.loaded = []
    
    def load_modules(self):
        if self.debug:
            self.log('** Checking modules in rules folder.')
        modules = {}
        walker = pkgutil.walk_packages(rules.__path__, rules.__name__ + '.')
        for tup in walker:
            name = tup[1]
            
            if self.debug:
                self.log('** Found module \'{0}\'.'.format(name))
                
            if name in self.modules.keys():
                if self.debug:
                    self.log('** Previously loaded ruleset. Reloading!')
                imp.reload(self.modules[name])
                modules[name] = self.modules[name]
                continue
                
            loader = pkgutil.find_loader(name)
            mod = loader.load_module(name)
            
            if not hasattr(mod, 'Ruleset'):
                if self.debug:
                    self.log('>> Ignoring ruleset module {0}.'.format(name))
                    self.log('>> Module contains no Ruleset class.')
                    continue
            
            modules[name] = mod
        self.modules = modules
    
    def load_rules(self, core, manager):
        if self.debug:
            self.log('** Loading rulesets...')
        self.load_modules()
        self.loaded = []
        for name, mod in self.modules.items():
            try:
                rulename = str(mod.__name__).split('.')[1]
                manager.define_rules(rulename, mod.Ruleset, core, manager)
                self.loaded.append(rulename)
            except Exception as e:
                self.log('>> Failed to load ruleset from {0}!'.format(name))
                self.log('>> Error: {0}'.format(e.args[0]))
        
        if self.debug:
            self.log('** Loaded rulesets: {0}'.format(', '.join(self.loaded)))
