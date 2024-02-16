import warnings

warnings.warn("The ansys.rep.client has been renamed to ansys.hps.client. Please update your import statement.", DeprecationWarning, stacklevel=2)

from ansys.hps.client import *