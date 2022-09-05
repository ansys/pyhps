import sys
import os
from .registry import registry
from .download import download

# no code completion when autogenerating the code
# thismodule = sys.modules[__name__]
# for k in registry:
#     setattr(thismodule, f"download_{os.path.splitext(k)[0]}", lambda: download(k))