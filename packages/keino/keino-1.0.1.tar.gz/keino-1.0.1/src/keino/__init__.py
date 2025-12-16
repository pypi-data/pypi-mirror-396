from .hash_dict import hash_dict
from .kpath import kpath, k_path
from .rounded_polygon import RoundedPolygon
from .params import Params
from .pprint_array import pprint
from .build_axes import *
from .versioned_import import versioned_import
from .add_colourbar import add_colourbar
from .copy_artist import copy_artist
from .ndindex import ndindex
from .int_path import int_path
from .vectorize_parallel import vectorize_parallel

from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("keino")
except PackageNotFoundError:
    # package is not installed
    pass
