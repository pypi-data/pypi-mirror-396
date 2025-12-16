# salutator/__init__.py
"""
Salutator — a package for greetings and goodbyes
across humans, animals, plants, and minerals.
"""

from . import humans
from . import animals
from . import plants
from . import minerals
from . import eso


#  Version info (__version__)
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0"


__all__ = ['humans', 'animals', 'plants', 'minerals', 'eso']

