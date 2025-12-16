"""pyvista4dolfinx: A simple plotting interface for DOLFINx using PyVista.

This package provides convenient plotting functions for DOLFINx finite element
computations, with MPI-safe implementations for parallel execution.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("pyvista4dolfinx")
except PackageNotFoundError:
    # Package is not installed
    __version__ = "unknown"

from .plot import plot, show, screenshot, reset_plotter
from .safeplotter import Plotter
from .misc import *
