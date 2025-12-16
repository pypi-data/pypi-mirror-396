# Copyright (C) 2025 Stein K.F. Stoter
#
# This file is part of pyvista4dolfinx
#
# SPDX-License-Identifier:    MIT

from functools import singledispatch, wraps
from typing import Any
import atexit

import basix
import dolfinx
from mpi4py import MPI
import numpy as np
import pyvista
import ufl.measure

from .safeplotter import Plotter
from .gather import _gather_grid, _gather_meshtags

__all__ = [
    "show",
    "screenshot",
    "reset_plotter",
    "plot",
    "plot_function_scalar",
    "plot_function_vector",
    "plot_mesh",
    "plot_meshtags",
    "plot_entities",
    "plot_dofs",
]

pyvista.global_theme.allow_empty_mesh = True


@wraps(Plotter.show)
def show(*args, auto_close: bool = None, **kwargs):
    global PLOTTER
    ret = PLOTTER.show(*args, auto_close=auto_close, **kwargs)
    if auto_close is not False:
        reset_plotter()
    return ret


_show = show
show.__name__ = "show"
show.__qualname__ = "show"
show.__doc__ = show.__doc__.split("Examples", 1)[0]  # Remove pyvista specific examples


@wraps(Plotter.screenshot)
def screenshot(filename: str, *args, **kwargs):
    global PLOTTER
    ret = PLOTTER.screenshot(filename, *args, **kwargs)
    reset_plotter()
    return ret


screenshot.__name__ = "screenshot"
screenshot.__qualname__ = "screenshot"
screenshot.__doc__ = screenshot.__doc__.split("Examples", 1)[
    0
]  # Remove pyvista specific examples


# Module global plotter object on rank 0. Empty plotter on all other ranks.
PLOTTER = Plotter()


def reset_plotter(*args, plotter: Plotter = None, **kwargs):
    """
    Reset the default module global `PLOTTER`. If specified, it is set to
    `plotter`. Otherwise, a new empty `Plotter` is created and arguments and
    keyword arguments passed are forwarded to the initialization of the new `Plotter`.

    Parameters
    ----------
    plotter : Plotter, optional
        If specified, the module global PLOTTER is set to this plotter,
        by default None
    """
    global PLOTTER
    PLOTTER = plotter if plotter is not None else Plotter(*args, **kwargs)


atexit.register(
    reset_plotter
)  # Mitigate python exiting conflict due to wrong PLOTTER state.


@singledispatch
def plot(plottable: Any, *args, **kwargs) -> Plotter:
    """
    Plots the plottable and returns the pyvista `Plotter` object. Depending
    on the type of the plottable, the call is dispatched to:

    >>> pyvista4dolfinx.plot.plot_function_scalar(plottable, *args, **kwargs)  # for scalar dolfinx.fem.Function
    >>> pyvista4dolfinx.plot.plot_function_vector(plottable, *args, **kwargs)  # for vector dolfinx.fem.Function
    >>> pyvista4dolfinx.plot.plot_mesh(plottable, *args, **kwargs)  # for dolfinx.mesh.Mesh
    >>> pyvista4dolfinx.plot.plot_meshtags(plottable, *args, **kwargs)  # for dolfinx.mesh.MeshTags
    >>> pyvista4dolfinx.plot.plot_measure(plottable, *args, **kwargs)  # for ufl.measure.Measure

    Parameters
    ----------
    plottable : dolfinx.fem.Function | dolfinx.mesh.Mesh | dolfinx.mesh.MeshTags
        The plottable entity.

    Returns
    -------
    Plotter
        An mpi-safe child of pyvista.Plotter.
    """
    raise NotImplementedError(
        f"Plotting objects of type {type(plottable)} not implemented"
    )


@plot.register
def plot_function_(plottable: dolfinx.fem.Function, *args, **kwargs) -> Plotter:
    # Check if this is a sub-function from a mixed element that needs collapsing
    # Subspaces have a non-empty component list
    if plottable.function_space.component():
        # This is a subspace from a mixed element - collapse it
        plottable = plottable.collapse()

    if len(plottable.ufl_shape) > 0:
        return plot_function_vector(plottable, *args, **kwargs)
    return plot_function_scalar(plottable, *args, **kwargs)


@plot.register
def plot_mesh_(
    plottable: dolfinx.mesh.Mesh,
    *args,
    show_partitioning: bool = False,
    **kwargs,
) -> Plotter:
    if show_partitioning:
        meshtags = _get_partitioning_meshtags(plottable)
        return plot_meshtags(meshtags, *args, mesh=plottable, name="MPI rank", **kwargs)
    return plot_mesh(plottable, *args, **kwargs)


@plot.register
def plot_meshtags_(plottable: dolfinx.mesh.MeshTags, *args, **kwargs) -> Plotter:
    return plot_meshtags(plottable, *args, **kwargs)


@plot.register
def plot_measure_(plottable: ufl.measure.Measure, *args, **kwargs) -> Plotter:
    return plot_measure(plottable, *args, **kwargs)


@plot.register
def plot_list_(plottable: list, *args, **kwargs) -> Plotter:
    """
    Dispatcher for lists. Handles DOF lists from mixed element spaces.
    """
    entity_type = kwargs.pop("entity_type", None)
    function_space = kwargs.pop("function_space", None)

    # Check if this is a list of numpy arrays for DOFs from mixed spaces
    if entity_type == "dofs" and all(
        isinstance(item, np.ndarray) for item in plottable
    ):
        if function_space is None:
            raise ValueError(
                "When plotting DOF list from mixed space, you must provide 'function_space' argument"
            )

        if not isinstance(function_space, (tuple, list)):
            raise ValueError(
                "When plotting DOF list from mixed space, 'function_space' must be a tuple or list "
                "of (mixed_subspace, collapsed_space)"
            )

        if len(function_space) != 2:
            raise ValueError(
                f"function_space tuple/list must have exactly 2 elements (mixed_subspace, collapsed_space), "
                f"got {len(function_space)}"
            )

        if len(plottable) != 2:
            raise ValueError(
                f"DOF list from mixed space must have exactly 2 arrays, got {len(plottable)}"
            )

        # Extract the collapsed space (second element) and corresponding DOFs
        _, collapsed_space = function_space
        _, collapsed_dofs = plottable

        # Forward to plot_dofs with the collapsed space and its DOFs
        return plot_dofs(
            collapsed_dofs, function_space=collapsed_space, *args, **kwargs
        )

    # Handle other list cases
    raise ValueError(
        "Plotting lists is only supported for DOF arrays from mixed element spaces. "
        "Ensure entity_type='dofs' and function_space is a tuple of (mixed_subspace, collapsed_space)."
    )


@plot.register
def plot_array_(plottable: np.ndarray, *args, **kwargs) -> Plotter:
    """
    Dispatcher for numpy arrays. Routes to appropriate plotting function based on entity_type.
    """
    entity_type = kwargs.pop("entity_type", None)
    mesh_arg = kwargs.get("mesh", None)
    function_space = kwargs.pop("function_space", None)

    if entity_type is None:
        raise ValueError(
            "When plotting a numpy array, you must specify 'entity_type'. "
            "Valid options: 'facets', 'cells', 'dofs'"
        )

    entity_type = entity_type.lower()

    if entity_type in ["facets", "cells", "elements"]:
        if mesh_arg is None:
            raise ValueError(
                f"When plotting entity_type='{entity_type}', you must provide 'mesh' argument"
            )
        return plot_entities(plottable, entity_type=entity_type, *args, **kwargs)
    elif entity_type == "dofs":
        if function_space is None:
            raise ValueError(
                "When plotting entity_type='dofs', you must provide 'function_space' argument"
            )
        return plot_dofs(plottable, function_space=function_space, *args, **kwargs)
    else:
        raise ValueError(
            f"Unknown entity_type '{entity_type}'. "
            "Valid options: 'facets', 'cells', 'dofs'"
        )


def plot_function_scalar(
    u: dolfinx.fem.Function,
    warp: dolfinx.fem.Function | bool = False,
    show_mesh: bool = True,
    name: str = "",
    plotter: Plotter | None = None,
    clear_plotter: bool = False,
    subplot: tuple | None = None,
    show: bool = False,
    **kwargs,
) -> Plotter:
    """
    Produce a contourplot of scalar-valued function `u`.

    Parameters
    ----------
    u : dolfinx.fem.Function
        The plotted scalar-valued function.
    warp: dolfinx.fem.Function | bool, optional
        Vector-valued function by which to warp the mesh. If `True`, it is
        assumed this is a 2D plot and the mesh is warped by `u` in the
        z-direction, by default False
    show_mesh: bool, optional
        Whether to overlay a plot of the mesh edges, by default True
    name : str, optional
        The name to give field `u` in the colorbar, by default ""
    plotter: Plotter | None, optional
        The Plotting object to which to add this data. If None, the default
        (module-level) instance is used, by default None
    clear_plotter : bool, optional
        Whether to clear/reset the default Plotter instance, by default
        False
    subplot : tuple | None, optional
        If the Plotter is initialized with multiple subplots, specify with
        a tuple which sublot to plot in, by default None
    show : bool, optional
        Whether to show upon completion. Alternatively, call `.show()` on
        the returned Plotter `instance`. By default False
    **kwargs
        The remaining keyword arguments are passed to the
        `plotter.add_mesh` call.

    Returns
    -------
    Plotter
        An mpi-safe child of pyvista.Plotter.
    """

    global PLOTTER
    if clear_plotter:
        reset_plotter()
    if subplot is not None:
        PLOTTER.subplot(*subplot)

    u, warp = _upgrade_u_and_warp_to_geometry(u, warp, min_degree=1)
    u, warp = _compatible_scalar_u_warp(u, warp)

    # Subdivide high-order geometry even without warp for smoother 2D plots
    _subdivide = (
        warp is False
        and hasattr(u.function_space.mesh, "geometry")
        and getattr(u.function_space.mesh.geometry, "cmap", None) is not None
        and getattr(u.function_space.mesh.geometry.cmap, "degree", 1) > 1
    )
    _preserve_shared_edges = _subdivide and warp is False

    # Gather data onto MPI process 0
    grid = _gather_grid(
        u.function_space.mesh,
        u,
        warp=warp,
        name=name,
        _force_high_order_subdivision=_subdivide,
    )
    # If we need to show mesh edges for a warped scalar plot, gather the
    # corresponding mesh grid before the MPI rank guard so all ranks
    # participate in the collective operations.
    mesh_grid_edges = None
    if show_mesh and (warp is True or type(warp) is not bool):
        mesh_grid_edges = _gather_grid(
            u.function_space.mesh, u, warp=warp, name=name, _no_subdivide=True
        )
    if MPI.COMM_WORLD.rank != 0:
        return PLOTTER

    # Set the global plotter
    PLOTTER = plotter if plotter is not None else PLOTTER

    # Default plotting options
    defaults = {"show_scalar_bar": True}

    # Visualize
    options = defaults | kwargs
    PLOTTER.add_mesh(grid, **options)
    if show_mesh:
        # Use the pre-gathered mesh grid to avoid MPI deadlocks
        if mesh_grid_edges is not None:
            _plot_feature_edges(PLOTTER, mesh_grid_edges)
        else:
            _plot_feature_edges(
                PLOTTER,
                grid,
                preserve_shared=_preserve_shared_edges,
            )
    if warp is not True and u.function_space.mesh.geometry.dim in [1, 2]:
        PLOTTER.view_xy()

    if show:
        _show()

    return PLOTTER


def plot_function_vector(
    u: dolfinx.fem.Function,
    warp: dolfinx.fem.Function | bool = False,
    show_mesh: bool = True,
    name: str = "",
    plotter: pyvista.Plotter | None = None,
    clear_plotter: bool = False,
    subplot: tuple | None = None,
    show: bool = False,
    glyph_resolution: int | None = None,
    **kwargs,
) -> Plotter:
    """
    Produce a glyph plot of `u`.

    Parameters
    ----------
    u : dolfinx.fem.Function.
        The plotted vector-valued function.
    warp: dolfinx.fem.Function | bool, optional
        Vector-valued function by which to warp the mesh. If
        `True`, the mesh is warped by `u`, by default False
    show_mesh: bool, optional
        Whether to overlay a plot of the mesh edges, by default True
    name : str, optional
        The name to give field `u` in the colorbar, by default ""
    plotter: Plotter | None, optional
        The Plotting object to which to add this data. If None, the default
        (module-level) instance is used, by default None
    clear_plotter : bool, optional
        Whether to clear/reset the default Plotter instance, by default
        False
    subplot : tuple | None, optional
        If the Plotter is initialized with multiple subplots, specify with
        a tuple which subplot to plot in, by default None
    show : bool, optional
        Whether to show upon completion. Alternatively, call `.show()` on
        the returned Plotter instance. By default False
    glyph_resolution : int | None, optional
        Subdivision level for curved geometry. If None, defaults to 0
        (no subdivision). Set to a positive integer for smooth curved
        visualization, by default None
    **kwargs
        The remaining keyword arguments are passed to the
        `plotter.add_mesh` call.

    Returns
    -------
    Plotter
        An mpi-safe child of pyvista.Plotter.
    """
    global PLOTTER
    if clear_plotter:
        reset_plotter()
    if subplot is not None:
        PLOTTER.subplot(*subplot)

    # Handle element types not supported by pyvista
    if u.ufl_element().family_name not in [
        "Discontinuous Lagrange",
        "Lagrange",
        "DQ",
        "Q",
        "DP",
        "P",
    ]:
        u = _interpolate_vector_DG(u)

    # For high-order geometry, upgrade vector field to match geometry degree
    # so glyphs are placed at subdivision points along curved boundaries
    try:
        geom_deg = u.function_space.mesh.geometry.cmap.degree
    except Exception:
        geom_deg = 1

    u, warp = _upgrade_u_and_warp_to_geometry(u, warp, min_degree=geom_deg)

    if type(warp) is not bool and warp.function_space != u.function_space:
        warp = _interpolate(warp, u.function_space)

    # Subdivide high-order geometry even without warp for smoother 2D glyph plots
    # Allow manual override via glyph_resolution parameter
    # Default behavior: no subdivision (glyph_resolution defaults to 0)
    if glyph_resolution is None:
        # Default: no subdivision
        _subdivide = False
    elif glyph_resolution == 0:
        _subdivide = False
    else:
        # Explicit positive value: enable subdivision if high-order geometry
        _subdivide = (
            warp is False
            and hasattr(u.function_space.mesh, "geometry")
            and getattr(u.function_space.mesh.geometry, "cmap", None) is not None
            and getattr(u.function_space.mesh.geometry.cmap, "degree", 1) > 1
        )

    # Gather data onto MPI process 0
    grid = _gather_grid(
        u.function_space.mesh,
        u,
        warp=warp,
        name=name,
        _force_high_order_subdivision=_subdivide,
        _subdivision_level=glyph_resolution,
    )

    # Plot outline
    gdim = u.function_space.mesh.geometry.dim
    if gdim == 2 and not show_mesh and warp is False:
        outline_meshtags = _get_outline_meshtags(u.function_space.mesh)
        plot_meshtags(
            outline_meshtags,
            mesh=u.function_space.mesh,
            tagvalue=1,
            warp=warp,
            plotter=plotter,
            color="black",
            line_width=1,
            show_scalar_bar=False,
            show_mesh=False,
            _skip_outline=True,
        )

    if MPI.COMM_WORLD.rank != 0:
        return PLOTTER

    # Set the global plotter
    PLOTTER = plotter if plotter is not None else PLOTTER

    # Manipulate grid data
    factor = kwargs.pop("factor") if "factor" in kwargs.keys() else 1
    glyphs = grid.glyph(orient=name if name else u.name, factor=factor)
    glyphs.rename_array("GlyphScale", name if name else u.name)

    # Default plotting options
    defaults = {"show_scalar_bar": True}

    # Visualize
    options = defaults | kwargs
    PLOTTER.add_mesh(glyphs, **options)  # Main operation
    if show_mesh and gdim in [2, 3]:
        _plot_feature_edges(PLOTTER, grid, preserve_shared=_subdivide)
    if gdim in [1, 2]:
        PLOTTER.view_xy()

    if show:
        _show()

    return PLOTTER


def plot_mesh(
    mesh: dolfinx.mesh.Mesh,
    warp: dolfinx.fem.Function | bool = False,
    plotter: pyvista.Plotter | None = None,
    clear_plotter: bool = False,
    subplot: tuple | None = None,
    show: bool = False,
    **kwargs,
) -> Plotter:
    """
    Produce a plot of the mesh.

    Parameters
    ----------
    mesh : dolfinx.mesh.Mesh
        Mesh to be plotted.
    warp: dolfinx.fem.Function | bool, optional
        Field by which to warp the mesh, by default False
    plotter: Plotter | None, optional
        The Plotting object to which to add this data. If None, the default
        (module-level) instance is used, by default None
    clear_plotter : bool, optional
        Whether to clear/reset the default Plotter instance, by default
        False
    subplot : tuple | None, optional
        If the Plotter is initialized with multiple subplots, specify with
        a tuple which sublot to plot in, by default None
    show : bool, optional
        Whether to show upon completion. Alternatively, call `.show()` on
        the returned Plotter `instance`. By default False
    **kwargs
        The remaining keyword arguments are passed to the
        `plotter.add_mesh` call.

    Returns
    -------
    Plotter
        An mpi-safe child of pyvista.Plotter.
    """
    global PLOTTER
    if clear_plotter:
        reset_plotter()
    if subplot is not None:
        PLOTTER.subplot(*subplot)

    # Gather data onto MPI process 0
    grid = _gather_grid(mesh, warp=warp)
    if MPI.COMM_WORLD.rank != 0:
        return PLOTTER

    # Set the global plotter
    PLOTTER = plotter if plotter is not None else PLOTTER

    # Default plotting options
    defaults = {"style": "wireframe", "color": "black"}

    # Visualize
    options = defaults | kwargs
    _plot_feature_edges(PLOTTER, grid, options=options)
    if mesh.geometry.dim in [1, 2]:
        PLOTTER.view_xy()

    if show:
        _show()

    return PLOTTER


def plot_meshtags(
    meshtags: dolfinx.mesh.MeshTags,
    mesh: dolfinx.mesh.Mesh | None = None,
    tagvalue: int | None = None,
    warp: None = None,
    show_mesh: bool = True,
    name: str = "Tags",
    plotter: pyvista.Plotter | None = None,
    clear_plotter: bool = False,
    subplot: tuple | None = None,
    show: bool = False,
    _skip_outline: bool = False,
    **kwargs,
) -> Plotter:
    """
    Produce a plot of the meshtags.

    Parameters
    ----------
    meshtags:  dolfinx.mesh.MeshTags
        Meshtags to be plotted
    mesh : dolfinx.mesh.Mesh | None, optional
        Mesh corresponding to the meshtags, by default None
    tagvalue: int | None, optional
        Which tag to show. If None, will show all tags, by default None
    warp: None, optional
        Reserved for future use; warping is not currently supported, by default None
    show_mesh: bool, optional
        Whether to overlay a plot of the mesh edges, by default True
    name : str, optional
        The name to give tags in the colorbar, by default "Tags"
    plotter: Plotter | None, optional
        The Plotting object to which to add this data. If None, the default
        (module-level) instance is used, by default None
    clear_plotter : bool, optional
        Whether to clear/reset the default Plotter instance, by default
        False
    subplot : tuple | None, optional
        If the Plotter is initialized with multiple subplots, specify with
        a tuple which subplot to plot in, by default None
    show : bool, optional
        Whether to show upon completion. Alternatively, call `.show()` on
        the returned Plotter instance. By default False
    _skip_outline : bool, optional
        Internal parameter to skip outline plotting (used for recursion), by default False
    **kwargs
        The remaining keyword arguments are passed to the
        `plotter.add_mesh` call.

    Returns
    -------
    Plotter
        An mpi-safe child of pyvista.Plotter.
    """
    global PLOTTER
    if clear_plotter:
        PLOTTER = Plotter()
    if subplot is not None:
        PLOTTER.subplot(*subplot)

    if mesh is None:
        raise ValueError(
            "A `mesh` must be supplied to plot meshtags. See help `plot_meshtags`."
        )
    if warp:
        raise NotImplementedError("Warping a meshtags object is not supported")

    meshtags_indices, meshtag_values = _gather_meshtags(meshtags, mesh, tag=tagvalue)
    grid = _gather_grid(mesh, dim=meshtags.dim, entities=meshtags_indices)
    # If we need to overlay the full mesh edges, gather the full mesh
    # grid before the MPI guard so all ranks participate.
    full_mesh_grid = None
    if show_mesh:
        full_mesh_grid = _gather_grid(mesh)

    # Plot outline
    gdim = mesh.geometry.dim
    if gdim == 2 and not show_mesh and not _skip_outline:
        outline_meshtags = _get_outline_meshtags(mesh)
        plot_meshtags(
            outline_meshtags,
            mesh=mesh,
            tagvalue=1,
            warp=warp,
            plotter=plotter,
            color="black",
            line_width=1,
            show_scalar_bar=False,
            show_mesh=False,
            _skip_outline=True,
        )

    if MPI.COMM_WORLD.rank != 0:
        return PLOTTER

    # Set the global plotter
    PLOTTER = plotter if plotter is not None else PLOTTER

    # Manipulate grid data
    grid.cell_data[name] = meshtag_values.astype(str)

    # Set plotting options:
    defaults = {"scalars": name, "show_edges": False, "show_scalar_bar": True}
    if meshtags.dim == 1:
        defaults |= {"line_width": 4}

    # Visualize
    options = defaults | kwargs
    gdim = mesh.geometry.dim
    PLOTTER.add_mesh(grid, **options)
    if show_mesh and gdim in [2, 3]:
        # Use the pre-gathered full mesh grid to avoid MPI deadlocks
        _plot_feature_edges(
            PLOTTER, full_mesh_grid if full_mesh_grid is not None else grid
        )
    if gdim in [1, 2]:
        PLOTTER.view_xy()

    if show:
        _show()

    return PLOTTER


def plot_entities(
    entities: np.ndarray,
    mesh: dolfinx.mesh.Mesh,
    entity_type: str,
    name: str = "Entities",
    tagvalue: int = 1,
    **kwargs,
) -> Plotter:
    """
    Plot a numpy array of entity indices (facets or cells) by creating a temporary meshtags.

    Parameters
    ----------
    entities : np.ndarray
        Array of entity indices to plot.
    mesh : dolfinx.mesh.Mesh
        The mesh containing the entities.
    entity_type : str
        Type of entities: "facets" or "cells"/"elements".
    name : str, optional
        Name to display in the plot, by default "Entities".
    tagvalue : int, optional
        Tag value to assign to the entities, by default 1.
    **kwargs
        Additional keyword arguments passed to plot_meshtags.

    Returns
    -------
    Plotter
        An mpi-safe child of pyvista.Plotter.
    """
    entity_type = entity_type.lower()

    # Determine entity dimension
    if entity_type == "facets":
        entity_dim = mesh.topology.dim - 1
    elif entity_type in ["cells", "elements"]:
        entity_dim = mesh.topology.dim
    else:
        raise ValueError(
            f"Invalid entity_type '{entity_type}'. Use 'facets' or 'cells'"
        )

    # Create meshtags from the entity array
    entities = np.asarray(entities, dtype=np.int32)
    values = np.full_like(entities, tagvalue, dtype=np.int32)

    # Create meshtags
    tags = dolfinx.mesh.meshtags(mesh, entity_dim, entities, values)

    # Forward to plot_meshtags
    return plot_meshtags(tags, mesh=mesh, tagvalue=tagvalue, name=name, **kwargs)


def plot_dofs(
    dofs: np.ndarray,
    function_space: dolfinx.fem.FunctionSpace,
    name: str = "DOFs",
    **kwargs,
) -> Plotter:
    """
    Plot a numpy array of DOF indices by visualizing their locations as points.

    Parameters
    ----------
    dofs : np.ndarray
        Array of DOF indices to plot.
    function_space : dolfinx.fem.FunctionSpace
        The function space containing the DOFs.
    name : str, optional
        Name to display in the plot, by default "DOFs".
    **kwargs
        Additional keyword arguments passed to the plotter.

    Returns
    -------
    Plotter
        An mpi-safe child of pyvista.Plotter.

    Raises
    ------
    NotImplementedError
        If the function space is a mixed function space, or if the element type
        does not support pointwise evaluation (e.g., RT, BDM, Nedelec/N1curl elements).
        For mixed spaces, use DOFs from a collapsed subspace instead.
    """
    global PLOTTER

    clear_plotter = kwargs.pop("clear_plotter", False)
    subplot = kwargs.pop("subplot", None)
    show = kwargs.pop("show", False)
    plotter = kwargs.pop("plotter", None)

    if clear_plotter:
        reset_plotter()
    if subplot is not None:
        PLOTTER.subplot(*subplot)

    # Check if this is a mixed function space or element without pointwise DOFs
    try:
        # Get DOF coordinates - this will fail for mixed spaces and special elements
        dof_coords = function_space.tabulate_dof_coordinates()
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "mixed" in error_msg:
            raise NotImplementedError(
                "Plotting DOFs from mixed function spaces is not supported. "
                "Use DOFs from a collapsed subspace instead. "
                "For example, if W is a mixed space: "
                "V, _ = W.sub(0).collapse(); "
                "dofs = fem.locate_dofs_topological((W.sub(0), V), fdim, facets); "
                "plot(dofs, function_space=(W.sub(0), V), entity_type='dofs')"
            ) from e
        elif "pointwise evaluation" in error_msg:
            # Get element family name for better error message
            element = function_space.element
            try:
                element_family = (
                    str(element.basix_element.family)
                    if hasattr(element, "basix_element")
                    else "unknown"
                )
            except:
                element_family = "unknown"
            raise NotImplementedError(
                f"Plotting DOFs from elements without pointwise evaluation is not supported. "
                f"Current element type: {element_family}. "
                f"Elements like RT, BDM, and Nedelec (N1curl) do not have point-based DOFs."
            ) from e
        raise

    # Select only the specified DOFs
    dofs = np.asarray(dofs, dtype=np.int32)
    selected_coords = dof_coords[dofs]

    # Gather data onto MPI process 0
    if MPI.COMM_WORLD.size > 1:
        # Gather all coordinates to rank 0
        all_coords = MPI.COMM_WORLD.gather(selected_coords, root=0)
        if MPI.COMM_WORLD.rank == 0:
            selected_coords = np.vstack(all_coords)

    # Gather mesh grid (collective operation - must be called on all ranks)
    mesh_grid = _gather_grid(function_space.mesh)

    if MPI.COMM_WORLD.rank != 0:
        return PLOTTER

    # Set the global plotter
    PLOTTER = plotter if plotter is not None else PLOTTER

    # Create pyvista point cloud
    point_cloud = pyvista.PolyData(selected_coords)

    # Add scalar field to color the points
    point_cloud[name] = np.arange(len(selected_coords))

    # Default plotting options for points
    defaults = {
        "render_points_as_spheres": True,
        "point_size": 10,
        "show_scalar_bar": False,
        "color": "red",
    }

    # Visualize
    options = defaults | kwargs
    PLOTTER.add_mesh(point_cloud, **options)

    # Also plot the mesh for context
    _plot_feature_edges(
        PLOTTER,
        mesh_grid,
        options={"show_scalar_bar": False, "color": "black", "opacity": 0.3},
    )

    if function_space.mesh.geometry.dim in [1, 2]:
        PLOTTER.view_xy()

    if show:
        _show()

    return PLOTTER


def plot_measure(
    measure: ufl.measure.Measure,
    mesh: dolfinx.mesh.Mesh | None = None,
    show_mesh: bool = False,
    name: str = "Measure",
    plotter: pyvista.Plotter | None = None,
    clear_plotter: bool = False,
    subplot: tuple | None = None,
    show: bool = False,
    **kwargs,
) -> Plotter:
    """
    Produce a plot of the measure by plotting the underlying meshtags.

    Parameters
    ----------
    measure: ufl.measure.Measure
        Measure to be plotted
    mesh : dolfinx.mesh.Mesh | None, optional
        Mesh corresponding to the measure, by default None
    show_mesh: bool, optional
        Whether to overlay a plot of the mesh edges, by default False
    name : str, optional
        The name to give measure in the colorbar, by default "Measure"
    plotter: Plotter | None, optional
        The Plotting object to which to add this data. If None, the default
        (module-level) instance is used, by default None
    clear_plotter : bool, optional
        Whether to clear/reset the default Plotter instance, by default
        False
    subplot : tuple | None, optional
        If the Plotter is initialized with multiple subplots, specify with
        a tuple which subplot to plot in, by default None
    show : bool, optional
        Whether to show upon completion. Alternatively, call `.show()` on
        the returned Plotter instance. By default False
    **kwargs
        The remaining keyword arguments are passed to the
        `plotter.add_mesh` call.

    Returns
    -------
    Plotter
        An mpi-safe child of pyvista.Plotter.
    """
    # Forwards to plot_meshtags

    if mesh is None:
        raise ValueError(
            "A `mesh` must be supplied to plot measures. See help `plot_measure`."
        )

    meshtags = _get_measure_meshtags(measure, mesh)
    tagvalue = (
        measure.subdomain_id() if not measure.subdomain_id() == "everywhere" else None
    )
    kwargs = {"show_edges": False} | kwargs
    return plot_meshtags(
        meshtags,
        mesh=mesh,
        tagvalue=tagvalue,
        show_mesh=show_mesh,
        name=name,
        plotter=plotter,
        show=show,
        clear_plotter=clear_plotter,
        subplot=subplot,
        **kwargs,
    )


def _plot_feature_edges(
    plotter: pyvista.Plotter,
    grid: pyvista.UnstructuredGrid,
    options: dict = {"show_scalar_bar": False, "color": "black"},
    subdivisions: int = 4,
    preserve_shared: bool = False,
):
    """
    Extract and plot feature edges from an unstructured grid.

    Parameters
    ----------
    plotter : pyvista.Plotter
        The plotter to add edges to
    grid : pyvista.UnstructuredGrid
        The grid to extract edges from
    options : dict, optional
        Options to pass to add_mesh for the edges, by default {"show_scalar_bar": False, "color": "black"}
    subdivisions : int, optional
        Number of subdivisions for nonlinear extraction, by default 4
    preserve_shared : bool, optional
        Whether to preserve shared edges between cells, by default False
    """
    base = grid if preserve_shared else grid.separate_cells()
    surface = base.extract_surface(nonlinear_subdivision=subdivisions)
    edges = surface.extract_feature_edges()
    plotter.add_mesh(edges, **options)


def _get_outline_meshtags(
    mesh: dolfinx.mesh.Mesh,
):
    """
    Create meshtags for the outline (exterior facets) of a mesh.

    Parameters
    ----------
    mesh : dolfinx.mesh.Mesh
        The mesh to create outline meshtags for

    Returns
    -------
    dolfinx.mesh.MeshTags
        Meshtags with value 1 for boundary facets, 0 for interior facets
    """
    tdim = mesh.topology.dim
    mesh.topology.create_entities(tdim - 1)
    mesh.topology.create_connectivity(tdim - 1, tdim)
    boundary_facets = dolfinx.mesh.exterior_facet_indices(mesh.topology)
    num_cells = mesh.topology.index_map(tdim - 1).size_local
    indices = np.arange(num_cells)
    values = np.zeros(num_cells, dtype=int)
    values[boundary_facets] = 1
    meshtags = dolfinx.mesh.meshtags(
        mesh,
        mesh.topology.dim - 1,
        indices,
        values,
    )
    return meshtags


def _get_partitioning_meshtags(mesh: dolfinx.mesh.Mesh) -> dolfinx.mesh.MeshTags:
    """
    Create element meshtags filled with the MPI ranks associated with
    each element.

    Parameters
    ----------
    mesh : dolfinx.mesh.Mesh
        The mesh to create partitioning meshtags for

    Returns
    -------
    dolfinx.mesh.MeshTags
        Meshtags with values corresponding to MPI rank ownership
    """
    num_cells = mesh.topology.index_map(mesh.topology.dim).size_local
    meshtags = dolfinx.mesh.meshtags(
        mesh,
        mesh.topology.dim,
        np.arange(num_cells),
        np.ones(num_cells, dtype=int) * MPI.COMM_WORLD.rank,
    )
    return meshtags


def _get_measure_meshtags(
    measure: ufl.Measure, mesh: dolfinx.mesh.Mesh
) -> dolfinx.mesh.MeshTags:
    """
    Obtain the meshtags associated with an integration measure. The values
    refer to the different integrable sub-measures.

    Parameters
    ----------
    measure : ufl.Measure
        The UFL measure to extract meshtags from
    mesh : dolfinx.mesh.Mesh
        The mesh associated with the measure

    Returns
    -------
    dolfinx.mesh.MeshTags
        Meshtags representing the integration domains
    """
    if type(measure.subdomain_data()) is dolfinx.mesh.MeshTags:
        return measure.subdomain_data()
    num_cells = mesh.topology.index_map(mesh.topology.dim).size_local
    meshtags = dolfinx.mesh.meshtags(
        mesh, mesh.topology.dim, np.arange(num_cells), np.ones(num_cells)
    )
    return meshtags


def _interpolate_vector_DG(u: dolfinx.fem.Function):
    """
    Interpolate a vector-valued field onto a DG superspace for
    visualization of advanced FE spaces.

    Parameters
    ----------
    u : dolfinx.fem.Function
        Vector-valued function to interpolate

    Returns
    -------
    dolfinx.fem.Function
        Interpolated function in Discontinuous Lagrange space
    """
    V = u.function_space
    domain = V.mesh
    gdim = domain.geometry.dim
    poldeg = V.element.basix_element.degree
    VDG = dolfinx.fem.functionspace(domain, ("Discontinuous Lagrange", poldeg, (gdim,)))
    return _interpolate(u, VDG)


def _interpolate(u: dolfinx.fem.Function, V: dolfinx.fem.FunctionSpace):
    """
    Basic interpolation helper.

    Parameters
    ----------
    u : dolfinx.fem.Function
        Function to interpolate
    V : dolfinx.fem.FunctionSpace
        Target function space

    Returns
    -------
    dolfinx.fem.Function
        Interpolated function in the target space
    """
    u_new = dolfinx.fem.Function(V, name=u.name)
    u_new.interpolate(u)
    return u_new


def _upgrade_u_and_warp_to_geometry(
    u: dolfinx.fem.Function, warp: dolfinx.fem.Function | bool, min_degree: int = 0
):
    """
    Upgrade `u` (and optional `warp`) to respect the mesh geometry degree.
    Both u and warp are upgraded to the same target degree to ensure compatibility.

    Parameters
    ----------
    u : dolfinx.fem.Function
        Function to upgrade
    warp : dolfinx.fem.Function | bool
        Warp function to upgrade, or bool flag
    min_degree : int, optional
        Minimum polynomial degree for the upgraded space, by default 0

    Returns
    -------
    tuple[dolfinx.fem.Function, dolfinx.fem.Function | bool]
        Upgraded u and warp functions
    """
    V = u.function_space
    domain = V.mesh
    try:
        geom_deg = max(domain.geometry.cmap.degree, min_degree)
    except Exception:
        geom_deg = max(1, min_degree)

    family_name = u.ufl_element().family_name
    discontinuous = u.ufl_element().discontinuous
    poldeg = V.element.basix_element.degree

    # Compute target degree from u and geometry
    target_deg = max(poldeg, geom_deg)

    # If warp is a function, also consider its degree in the target
    if type(warp) is not bool:
        warp_poldeg = warp.function_space.element.basix_element.degree
        target_deg = max(target_deg, warp_poldeg)

    # Upgrade u if needed
    if target_deg > poldeg:
        value_shape = u.ufl_element().reference_value_shape
        shape = None if value_shape in [(), (1,)] else value_shape
        el_up = basix.ufl.element(
            family_name,
            domain.ufl_cell().cellname(),
            target_deg,
            shape=shape,
            discontinuous=discontinuous,
        )
        V = dolfinx.fem.functionspace(domain, el_up)
        u = _interpolate(u, V)

    if type(warp) is bool:
        return u, warp

    # Upgrade warp to match u's target degree
    warp_poldeg = warp.function_space.element.basix_element.degree
    if (
        warp_poldeg < target_deg
        or warp.ufl_element().family_name != family_name
        or warp.ufl_element().discontinuous != discontinuous
    ):
        warp_shape = warp.ufl_element().reference_value_shape
        shape = None if warp_shape in [(), (1,)] else warp_shape
        el_warp = basix.ufl.element(
            family_name,
            domain.ufl_cell().cellname(),
            target_deg,
            shape=shape,
            discontinuous=discontinuous,
        )
        Vwarp = dolfinx.fem.functionspace(domain, el_warp)
        warp = _interpolate(warp, Vwarp)

    return u, warp


def _compatible_scalar_u_warp(
    u: dolfinx.fem.Function, warp: dolfinx.fem.Function | bool
):
    """
    Ensure that the scalar u field and the warp field can be plotted on
    the same mesh. Essentially, the warp field is projected onto the
    function space of a vectorized u.

    Parameters
    ----------
    u : dolfinx.fem.Function
        Scalar function
    warp : dolfinx.fem.Function | bool
        Warp function or bool flag

    Returns
    -------
    tuple[dolfinx.fem.Function, dolfinx.fem.Function | bool]
        Compatible u and warp functions
    """
    V = u.function_space
    domain = V.mesh

    if type(warp) == bool:
        return u, warp

    family_name = u.ufl_element().family_name
    discontinuous = u.ufl_element().discontinuous
    poldeg = V.element.basix_element.degree
    try:
        geom_deg = domain.geometry.cmap.degree
    except Exception:
        geom_deg = 1
    gdim = domain.geometry.dim
    target_deg = max(poldeg, geom_deg)

    if (
        warp.ufl_element().family_name != family_name
        or warp.function_space.element.basix_element.degree < target_deg
        or warp.ufl_element().discontinuous != discontinuous
        or warp.ufl_element().reference_value_shape != (gdim,)
    ):
        el = basix.ufl.element(
            family_name,
            domain.ufl_cell().cellname(),
            target_deg,
            shape=(gdim,),
            discontinuous=discontinuous,
        )
        Vwarp = dolfinx.fem.functionspace(domain, el)
        warp = _interpolate(warp, Vwarp)

    return u, warp
