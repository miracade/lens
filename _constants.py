# _constants.py

from enum import Enum


class FILE_EXT(Enum):
    """
    Enum for the file extensions used by Lens.
    """

    COMPILABLE = "lcom"
    ASSEMBLY = "lasm"
    BYTECODE = "lbin"
