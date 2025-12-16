# Copyright (C) 2025 Stein K.F. Stoter
#
# This file is part of pyvista4dolfinx
#
# Credit to Jørgen S. Dokken and Garth N. Wells
#
# SPDX-License-Identifier:    MIT

import dolfinx, pyvista, numpy as np


def _gather_grid(
    mesh: dolfinx.mesh.Mesh,
    u: dolfinx.fem.Function | None = None,
    warp: dolfinx.fem.Function | bool = False,
    name: str = "",
    dim: int | None = None,
    entities: np.typing.NDArray | None = None,
    _no_subdivide: bool = False,
    _force_high_order_subdivision: bool = False,
    _subdivision_level: int | None = None,
) -> pyvista.UnstructuredGrid | None:
    """
    Create an unstructured grid filled with field values associated with
    `u`, warped by the `warp` vector, obtained from gathering the data from
    all processes onto rank 0.

    Parameters
    ----------
    mesh : dolfinx.mesh.Mesh
        Mesh associated with `u` and `warp`.
    u : dolfinx.fem.Function | None, optional
        Function field from which to obtain the grid, by default None
    warp: dolfinx.fem.Function | bool, optional
        Vector-valued function field by which to warp the mesh, by default False
    name: str, optional
        Name to give the data in the mesh. If empty string, the name
        of the `u` field is used, by default ""
    dim: int | None, optional
        Dimension of the grid to be extracted (e.g., for obtaining a
        wireframe for a 2D mesh). None means the topological dimension,
        by default None
    entities: np.typing.NDArray | None, optional
        Entity indices to extract from the entire mesh for plotting mesh
        segments. None means all entities, by default None
    _no_subdivide : bool, optional
        Internal flag to disable subdivision, by default False
    _force_high_order_subdivision : bool, optional
        Internal flag to force subdivision for high-order geometry, by default False
    _subdivision_level: int | None, optional
        Explicit subdivision level for nonlinear_subdivision. If None,
        auto-detects based on mesh size, by default None

    Returns
    -------
    pyvista.UnstructuredGrid | None
        Only returns the `pyvista.UnstructuredGrid` object on
        `MPI.COMM_WORLD.rank == 0`, else `None`.
    """
    # See: https://fenicsproject.discourse.group/t/how-to-collect-the-global-mesh-without-writing-a-file/12445/3

    # Correct objects on which to operate for given input
    vtk_mesh_from = (
        mesh
        if u is None and type(warp) == bool
        else u.function_space if u is not None else warp.function_space
    )
    index_map_plottable = (
        vtk_mesh_from.geometry.index_map()
        if vtk_mesh_from is mesh
        else vtk_mesh_from.dofmap.index_map
    )
    dim_ = mesh.topology.dim if dim is None else dim
    if not name and u is not None:
        name = u.name

    # Create local VTK mesh data structures)
    topology, cell_types, geometry = (
        np.empty((0,), dtype=np.int32),
        np.empty((0,)),
        np.empty((0, 3)),
    )
    if entities is None or len(entities) > 0:
        args = (
            [vtk_mesh_from, dim, entities] if vtk_mesh_from is mesh else [vtk_mesh_from]
        )
        topology, cell_types, geometry = dolfinx.plot.vtk_mesh(*args)
        num_cells_local = mesh.topology.index_map(dim_).size_local
        num_cells_local_geom = index_map_plottable.size_local

        # Restructure topology vector in case of parallel execution
        num_dofs_per_cell = topology[0]
        topology_dofs = (np.arange(len(topology)) % (num_dofs_per_cell + 1)) != 0
        global_dofs = index_map_plottable.local_to_global(
            topology[topology_dofs].copy()
        )
        topology[topology_dofs] = global_dofs

        # Final data shapes
        topology = topology[: (num_dofs_per_cell + 1) * num_cells_local]
        geometry = geometry[:num_cells_local_geom, :]
        cell_types = cell_types[:num_cells_local]

    # Gather mesh data
    global_topology = mesh.comm.gather(topology, root=0)
    global_geometry = mesh.comm.gather(geometry, root=0)
    global_cell_types = mesh.comm.gather(cell_types, root=0)

    # Gather function data
    if u is not None:
        V = u.function_space
        u_dim = u.ufl_shape[0] if len(u.ufl_shape) > 0 else 1
        num_dofs_local = V.dofmap.index_map.size_local * V.dofmap.index_map_bs
        global_vals = mesh.comm.gather(u.x.array[:num_dofs_local], root=0)

    # Gather warp function data
    if type(warp) is not bool:
        V_warp = warp.function_space
        warp_dim = warp.ufl_shape[0] if len(warp.ufl_shape) > 0 else 1
        num_dofs_local_warp = (
            V_warp.dofmap.index_map.size_local * V_warp.dofmap.index_map_bs
        )
        global_warp = mesh.comm.gather(warp.x.array[:num_dofs_local_warp], root=0)

    if mesh.comm.rank == 0:
        # Stack data
        root_geom = np.vstack(global_geometry)
        root_top = np.concatenate(global_topology)
        root_ct = np.concatenate(global_cell_types)

        # Create and fill the unstructured grid
        grid = pyvista.UnstructuredGrid(root_top, root_ct, root_geom)

        # Add u field to grid
        if u is not None:
            # Restructure values vector
            root_vals = np.concatenate(global_vals)
            num_dofs = root_geom.shape[0]
            if u_dim == 1:
                # For scalar fields, store as 1D array to preserve sign in color mapping
                values = root_vals.reshape(num_dofs, V.dofmap.index_map_bs).flatten()
            else:
                # For vector fields, store as 3D vectors
                values = np.zeros((num_dofs, 3), dtype=np.float64)
                values[:, :u_dim] = root_vals.reshape(num_dofs, V.dofmap.index_map_bs)
            grid.point_data[name] = values
            grid.set_active_scalars(name)

        # Add warp field to grid
        if type(warp) is not bool:
            root_warp = np.concatenate(global_warp)
            num_dofs = len(root_warp) // V_warp.dofmap.index_map_bs
            values_warp = np.zeros((num_dofs, 3), dtype=np.float64)
            values_warp[:, :warp_dim] = root_warp.reshape(num_dofs, warp_dim)
            grid.point_data["warp"] = values_warp

        # Warp the grid
        if type(warp) is not bool:
            grid = grid.warp_by_vector("warp")
        elif warp:
            if u_dim == mesh.geometry.dim:
                grid = grid.warp_by_vector(name)
            elif u_dim == 1 and mesh.geometry.dim in [1, 2]:
                # For 2D scalar fields, use nonlinear subdivision before warping
                # to create smooth visualization of high-order functions
                # Only apply if mesh is coarse and subdivision is not disabled
                num_cells = grid.n_cells
                if (
                    not _no_subdivide and num_cells < 500
                ):  # Only subdivide coarse meshes
                    # Calculate subdivision level based on mesh coarseness
                    # Fewer cells -> more subdivision needed
                    if num_cells < 50:
                        subdivisions = 4
                    elif num_cells < 200:
                        subdivisions = 3
                    else:
                        subdivisions = 2

                    # Extract surface with nonlinear subdivision for smooth representation
                    # This properly handles high-order function values
                    surface = grid.extract_surface(nonlinear_subdivision=subdivisions)
                    grid = surface.warp_by_scalar(name)
                else:
                    # No subdivision needed for fine meshes or when disabled
                    grid = grid.warp_by_scalar(name)
            else:
                raise NotImplementedError
        elif _force_high_order_subdivision:
            # Improve visuals for higher-order geometry even without warp
            try:
                geom_degree = mesh.geometry.cmap.degree
            except Exception:
                geom_degree = 1
            if geom_degree > 1 and mesh.topology.dim in [1, 2]:
                # Use explicit subdivision level if provided, otherwise auto-detect
                if _subdivision_level is not None:
                    subdivisions = _subdivision_level
                else:
                    num_cells = grid.n_cells
                    if num_cells < 50:
                        subdivisions = 4
                    elif num_cells < 200:
                        subdivisions = 3
                    elif num_cells < 500:
                        subdivisions = 2
                    else:
                        subdivisions = 1
                surface = grid.extract_surface(nonlinear_subdivision=subdivisions)
                grid = surface.cast_to_unstructured_grid()

        return grid


def _gather_meshtags(
    meshtags: dolfinx.mesh.MeshTags, mesh: dolfinx.mesh.Mesh, tag: int | None = None
) -> list[np.typing.NDArray, np.typing.NDArray]:
    """
    Gather the values of a `MeshTags` object on process 0. Returns the
    rank-local indices for each process and the gathered values on process 0.

    Parameters
    ----------
    meshtags : dolfinx.mesh.MeshTags
        The meshtags object to gather
    mesh : dolfinx.mesh.Mesh
        The mesh that the meshtags object refers to
    tag : int | None, optional
        Specific tag value to extract. `None` means all tags, by default None

    Returns
    -------
    list[np.typing.NDArray, np.typing.NDArray]
        [local_indices, root_values].
        root_values is `None` on all MPI ranks other than 0.
    """
    local_indices = np.copy(meshtags.indices)
    local_values = np.copy(meshtags.values)

    # Mask non-tagged and ghost
    mask = np.full_like(local_indices, True, dtype=np.bool_)
    index_map = mesh.topology.index_map(meshtags.dim)
    local_ghost_indices = index_map.global_to_local(index_map.ghosts)
    ghosts_ind = np.isin(local_indices, local_ghost_indices)
    mask[ghosts_ind] = False
    if tag:
        mask[local_values != tag] = False
    local_indices = local_indices[mask]
    local_values = local_values[mask]

    gathered_values = mesh.comm.gather(local_values, root=0)
    if mesh.comm.rank == 0:
        root_values = np.concatenate(gathered_values)
        return local_indices, root_values
    return local_indices, None
