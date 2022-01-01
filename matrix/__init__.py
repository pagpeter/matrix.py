"""
Matrix API wrapper.
===================


A basic wrapper for the Matrix API.

Copyright: (c) 2021-present, Peet 

License: MIT, see LICENSE for more details.

"""

__title__ = "matrix"
__author__ = "Peet"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2020-present Peet"
__version__ = "0.0.1"


from typing import Literal, NamedTuple
from .discord_like_classes import *
from .exceptions import *
from .constants import *
# from .classes import *
from .client import *
from .parsers import *
from .utils import *
from .e2ee import *

class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int 

version_info = VersionInfo(0, 0, 1, "alpha", 0)

