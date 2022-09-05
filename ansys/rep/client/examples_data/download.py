# until we don't sort out how to deal with the GitHub Auth token,
# we mock the download function just pointing to the 
# files distributed with the package 

import os

def download(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, "data", file_name)

### pooch implementation ###############################################################

# import pooch
# from .registry import registry
# from ansys.rep.client import __version__

# _downloader = pooch.create(
#     # Folder where the data will be stored. For a sensible default, use the
#     # default cache folder for your OS.
#     path=pooch.os_cache("ansys-rep-client"),
#     # Base URL of the remote data store. Will call .format on this string
#     # to insert the version (see below).
#     base_url="https://raw.githubusercontent.com/pyansys/pyrep/{version}/examples/data/",
#     # Pooches are versioned so that you can use multiple versions of a
#     # package simultaneously. Use PEP440 compliant version number. The
#     # version will be appended to the path.
#     version=f"v{__version__}+12",
#     # If a version as a "+XX.XXXXX" suffix, we'll assume that this is a dev
#     # version and replace the version with this string.
#     version_dev="fnegri/examples_pooch", # TODO should become "main" once merged 
#     # An environment variable that overwrites the path.
#     env="ANSYS_REP_CLIENT_DATA_DIR",
#     # The cache file registry. A dictionary with all files managed by this
#     # pooch. Keys are the file names (relative to *base_url*) and values
#     # are their respective SHA256 hashes. Files will be downloaded
#     # automatically when needed (see fetch_gravity_data).
#     registry=registry
# )

# def download(file_name):
#     return _downloader.fetch(file_name)
#####################################################################################