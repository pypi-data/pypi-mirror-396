import inspect
import os
from typing import List


def includes() -> str:
    """
    Returns: Path to a directory containing lots of header files.
    """
    dirname = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(dirname, "include")


def licenses() -> str:
    """
    Returns: Path to a directory containing licenses for each library.
    """
    dirname = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(dirname, "licenses")

