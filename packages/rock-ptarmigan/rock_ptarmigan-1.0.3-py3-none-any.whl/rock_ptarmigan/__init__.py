from importlib.metadata import version

from .main import compare_all
from .main import compare_train
from .main import compare_validation

# function call
__all__ = ['compare_all']
__all__ = ['compare_train']
__all__ = ['compare_validation']

# version
__version__ = version(__package__)
