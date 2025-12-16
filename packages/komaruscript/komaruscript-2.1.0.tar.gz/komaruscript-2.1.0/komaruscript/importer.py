import sys
import os
import importlib.abc
import importlib.util
from .transpiler import KomaruTranspiler

class KomaruMetaFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if path is None:
            path = sys.path
            
        # Handle dot imports (package.module)
        parts = fullname.split('.')
        module_name = parts[-1]
        
        # Look for .ks file
        for entry in path:
            if not isinstance(entry, str): continue
            
            ks_path = os.path.join(entry, module_name + ".ks")
            if os.path.exists(ks_path):
                return importlib.util.spec_from_file_location(
                    fullname, ks_path,
                    loader=KomaruLoader(ks_path)
                )
        return None

class KomaruLoader(importlib.abc.Loader):
    def __init__(self, path):
        self.path = path
        self.transpiler = KomaruTranspiler()

    def create_module(self, spec):
        return None  # Default behavior

    def exec_module(self, module):
        with open(self.path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        py_code = self.transpiler.transpile(code)
        
        # Inject stdlib path for dependencies
        stdlib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stdlib')
        if stdlib_path not in sys.path:
            sys.path.append(stdlib_path)
            
        exec(py_code, module.__dict__)

def install():
    sys.meta_path.insert(0, KomaruMetaFinder())
