import numpy                as     np
import sympy                as     sp
from   sympy                import latex
from   IPython.display      import Math, display
import matplotlib.pyplot    as     plt
import plotly.graph_objects as     go

def plot_3d(exprs, var, labels=None, colors=None,
            title="3D Plot", xlabel="x", ylabel="y", zlabel="Value",
            xlim=None, ylim=None, zlim=None,
            resolution=100, show=True):
    """
    Plots 3D surfaces from symbolic expressions using Plotly.

    Parameters:
    - exprs     : List of SymPy expressions or a single expression
    - var       : Tuple (x_sym, x_range, y_sym, y_range)
    - labels    : List of labels (LaTeX strings) for each surface
    - colors    : List of colors per surface
    - title     : Plot title
    - xlabel, ylabel, zlabel: Axis labels
    - xlim, ylim, zlim: Axis limit tuples
    - resolution: Grid resolution (default: 100x100)
    - show      : If True, shows the plot immediately

    Returns:
    - fig       : Plotly Figure object (if show=False)
    """

    if not isinstance(exprs, list):
        exprs = [exprs]

    if not isinstance(var, tuple) or len(var) != 4:
        raise ValueError("`var` must be a tuple: (x_sym, x_range, y_sym, y_range)")

    x_sym, x_range, y_sym, y_range = var

    x_vals = np.linspace(float(x_range[0]), float(x_range[1]), resolution)
    y_vals = np.linspace(float(y_range[0]), float(y_range[1]), resolution)
    X, Y   = np.meshgrid(x_vals, y_vals)

    fig = go.Figure()

    for i, expr in enumerate(exprs):
        expr  = sp.sympify(expr)
        color = colors[i] if colors and i < len(colors) else None
        label = labels[i] if labels and i < len(labels) else f"Expr {i+1}"

        f = sp.lambdify((x_sym, y_sym), expr, modules="numpy")
        Z = f(X, Y)
        if np.isscalar(Z):
            # Convert scalar zero (or any scalar) into a 2D array matching X,Y shape
            Z = np.zeros_like(X, dtype=float)

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            name=label,
            colorscale='Turbo' if color is None else [[0, color], [1, color]],
            showscale=False,
            opacity=0.9
        ))

    fig.update_layout(
        title=title,
        width=800, height=600,
        scene=dict(
            xaxis_title=xlabel,
            yaxis_title=ylabel,
            zaxis_title=zlabel,
            xaxis=dict(range=list(xlim) if xlim else None),
            yaxis=dict(range=list(ylim) if ylim else None),
            zaxis=dict(range=list(zlim) if zlim else None),
            aspectratio=dict(x=1, y=1, z=0.5),
            camera=dict(eye=dict(x=1.2, y=1.2, z=0.6))
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(x=0, y=1)
    )

    if show:
        fig.show()
        
    return fig
