import pyvista
from .plot import reset_plotter

__all__ = ["set_interactive"]


def set_interactive(state: bool = True):
    """
    Change settings to switch from interactive to non-interactive plots.

    If `state` is `True`, this runs:

    >>> pyvista.OFF_SCREEN = False
    >>> pyvista4dolfinx.reset_plotter()

    If `state` is `False` (this requires a renderable screen to be configured;
    on Unix systems requiring `libgl1-mesa-dev` and `mesa-utils`), this runs:

    >>> pyvista.OFF_SCREEN = True
    >>> pyvista4dolfinx.reset_plotter()

    Parameters
    ----------
    state : bool, optional
        Whether to activate or deactivate interactive plots, by default True
    """
    if state:
        pyvista.OFF_SCREEN = False
        reset_plotter()
    else:
        pyvista.OFF_SCREEN = True
        reset_plotter()
