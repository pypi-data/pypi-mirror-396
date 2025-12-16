__version__ = "2.1.0"

from .importer import install

# Auto-install import hook when package is imported
install()
