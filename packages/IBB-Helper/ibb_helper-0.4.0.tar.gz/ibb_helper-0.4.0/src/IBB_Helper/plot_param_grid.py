import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

def plot_param_grid(surface_exprs, var, control_points=None, cp_dims=None,
                         plot_cage=True, grid_lines=11,
                         title="Parametric Surface Grid",
                         xlabel="X", ylabel="Y", xlim=None, ylim=None,
                         grid_color='blue', points_color='red', cage_color='red',
                         points_label='Control Points',
                         figsize=(8, 6),
                         show=True):
    """
    Plots a 2D parametric surface's isoparametric grid and its control points.

    Parameters:
    - surface_exprs  : A list/tuple of two symbolic expressions [X(u,v), Y(u,v)].
    - var            : A tuple defining parameters and ranges: (u_sym, u_range, v_sym, v_range).
    - control_points : Optional. A Matrix or array of control point coordinates (shape: N x 2).
    - cp_dims        : Optional but needed for cage. A tuple (num_rows, num_cols) 
                       describing the grid layout of control points (e.g., (ny, nx)).
    - plot_cage      : If True, connects control points to form a cage.
    - grid_lines     : The number of isoparametric lines to draw in each direction.
    - title          : The plot's title.
    - xlabel, ylabel : Axis labels.
    - xlim, ylim     : Axis limits, e.g., (-1, 1).
    - grid_color     : Color of the isoparametric grid lines.
    - points_color   : Color of the control points.
    - cage_color     : Color of the control cage lines.
    - show           : If True, display the plot immediately.
    
    Returns:
    - fig, ax        : The matplotlib Figure and Axes objects.
    """

    if not isinstance(surface_exprs, (list, tuple)) or len(surface_exprs) != 2:
        raise ValueError("`surface_exprs` must be a list of two symbolic expressions.")
    
    if not isinstance(var, tuple) or len(var) != 4:
        raise ValueError("`var` must be a tuple: (u_sym, u_range, v_sym, v_range)")

    u_sym, u_range, v_sym, v_range = var
    
    fig, ax = plt.subplots(figsize=figsize) # <-- Use the new argument

    if control_points is not None:
        if isinstance(control_points, sp.Matrix):
            list_of_lists = control_points.tolist()
            cp_array = np.array(list_of_lists).astype(np.float64)
        else:
            cp_array = np.array(control_points)
        
        ax.plot(cp_array[:, 0], cp_array[:, 1], 'o', 
                color=points_color, markersize=10, label=points_label)

        if plot_cage:
            if cp_dims and len(cp_dims) == 2:
                num_rows, num_cols = cp_dims
                points_grid = cp_array.reshape(num_rows, num_cols, 2)
                for i in range(num_rows):
                    ax.plot(points_grid[i, :, 0], points_grid[i, :, 1], '-', 
                            color=cage_color, alpha=0.5, linewidth=1.5)
                for j in range(num_cols):
                    ax.plot(points_grid[:, j, 0], points_grid[:, j, 1], '-', 
                            color=cage_color, alpha=0.5, linewidth=1.5)
            else:
                 print("Warning: `cp_dims` (e.g., (ny, nx)) must be provided to plot the control cage.")

    u_param = np.linspace(float(u_range[0]), float(u_range[1]), 50)
    v_param = np.linspace(float(v_range[0]), float(v_range[1]), 50)
    u_grid = np.linspace(float(u_range[0]), float(u_range[1]), grid_lines)
    v_grid = np.linspace(float(v_range[0]), float(v_range[1]), grid_lines)
    
    expr_X = surface_exprs[0]
    expr_Y = surface_exprs[1]

    for v_const in v_grid:
        X_coords = [expr_X.subs({u_sym: u, v_sym: v_const}).evalf() for u in u_param]
        Y_coords = [expr_Y.subs({u_sym: u, v_sym: v_const}).evalf() for u in u_param]
        ax.plot(X_coords, Y_coords, color=grid_color, linewidth=2)

    for u_const in u_grid:
        X_coords = [expr_X.subs({u_sym: u_const, v_sym: v}).evalf() for v in v_param]
        Y_coords = [expr_Y.subs({u_sym: u_const, v_sym: v}).evalf() for v in v_param]
        ax.plot(X_coords, Y_coords, color=grid_color, linewidth=2)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if xlim: ax.set_xlim(xlim)
    if ylim: ax.set_ylim(ylim)
    ax.grid(True)
    
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend()
    
    ax.set_aspect('equal', adjustable='box')
    if show:
        plt.show()

    return fig, ax