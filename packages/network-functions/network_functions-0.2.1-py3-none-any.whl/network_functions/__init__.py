# Import the submodules so we can reference their __all__
from . import functions as _functions
from . import classifiers as _classifiers

# Re-export only the selected symbols
from .functions import *      # respects functions.__all__
from .classifiers import *    # respects classifiers.__all__

from importlib.metadata import version, PackageNotFoundError

# Build the package-level __all__
__all__ = list(getattr(_functions, "__all__", [])) + ["classifiers"]

_DIST_NAME = "network-functions"

try:
    __version__ = version(_DIST_NAME)
except PackageNotFoundError:
    # Fallback for local editable installs before the dist is built
    __version__ = "0+unknown"

