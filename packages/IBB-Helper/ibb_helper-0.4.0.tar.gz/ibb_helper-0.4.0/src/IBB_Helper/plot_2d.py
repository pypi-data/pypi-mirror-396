import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from sympy import latex, Matrix

def plot_2d(exprs, var, labels=None, line_styles=None, colors=None,
            title="2D Plot", xlabel="x", ylabel="y",
            xlim=None, ylim=None, resolution=400, show=True):
    """
    Plots 2D curves from symbolic expressions or (x, y) datasets using Matplotlib.
    Supports markers for control points and automatically evaluates symbolic expressions.
    """

    def smart_label(lbl):
        if isinstance(lbl, str):
            if "\\" in lbl:
                return f"${lbl}$"
            else:
                return lbl
        else:
            return f"${latex(lbl)}$"

    if not isinstance(exprs, list):
        exprs = [exprs]

    # Determine symbol and range
    if isinstance(var, tuple):
        x_sym = var[0]
        x_range = var[1]
    else:
        x_sym = var
        x_range = (-1, 1)

    x_vals_sample = np.linspace(float(x_range[0]), float(x_range[1]), resolution)

    fig, ax = plt.subplots()

    marker_symbols = ['o', 's', '^', 'x', '*', 'D', 'p', '+', 'v', '<', '>', '1', '2', '3', '4']

    for i, expr in enumerate(exprs):
        style = line_styles[i] if line_styles and i < len(line_styles) else 'solid'
        color = colors[i] if colors and i < len(colors) else None
        label = smart_label(labels[i]) if labels and i < len(labels) else None

        raw_label = labels[i] if labels and i < len(labels) else None
        label = smart_label(raw_label) if raw_label is not None else None

        marker = None

        # Convert SymPy Matrix to NumPy array
        if isinstance(expr, Matrix):
            expr = np.array(expr).astype(np.float64).flatten()

        # Tuple/list of two items (x, y)
        if isinstance(expr, (tuple, list)) and len(expr) == 2:
            x_data, y_data = expr

            # If symbolic expressions, lambdify automatically
            if isinstance(x_data, sp.Basic) or isinstance(y_data, sp.Basic):
                f_x = sp.lambdify(x_sym, x_data, modules='numpy')
                f_y = sp.lambdify(x_sym, y_data, modules='numpy')
                x_data = f_x(x_vals_sample)
                y_data = f_y(x_vals_sample)

            # If constant parametric plot
                is_x_array = hasattr(x_data, '__len__')
                is_y_array = hasattr(y_data, '__len__')

                if is_x_array and not is_y_array:
                    y_data = np.full_like(x_data, y_data)
                elif not is_x_array and is_y_array:
                    x_data = np.full_like(y_data, x_data)
 
            # If style is a marker, use it
            if style in marker_symbols:
                marker = style
                style = ''  # no line

            ax.plot(x_data, y_data, label=label, linestyle=style, color=color, marker=marker)

        else:
            # Single symbolic or numeric expression
            expr = sp.sympify(expr)
            if not expr.has(x_sym):
                y_vals = np.full_like(x_vals_sample, float(expr))
            else:
                f = sp.lambdify(x_sym, expr, modules='numpy')
                y_vals = np.array(f(x_vals_sample)).flatten()
            ax.plot(x_vals_sample, y_vals, label=label, linestyle=style, color=color, marker=marker)

    ax.set_title(smart_label(title))
    ax.set_xlabel(smart_label(xlabel))
    ax.set_ylabel(smart_label(ylabel))

    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    if labels:
        ax.legend()
    ax.grid(True)

    if show:
        plt.show()
    else:
        plt.close()

    return ax
