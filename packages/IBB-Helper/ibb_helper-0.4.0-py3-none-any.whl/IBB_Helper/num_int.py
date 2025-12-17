import numpy as np
from sympy import lambdify, Matrix, Float
from numpy.polynomial.legendre import leggauss

def num_int(expr, x_sym, x_range, n_intervals=10000, points_per_interval=1):
    """
    Composite Gauss-Legendre numeric integration over [a, b].
    
    Parameters
    ----------
    expr : sympy.Expr, list, or sympy.Matrix
        The expression(s) to integrate.
    x_sym : sympy.Symbol
        The integration variable.
    x_range : tuple (float, float)
        The interval (a, b).
    n_intervals : int
        Number of sub-elements to divide the domain into.
    points_per_interval : int
        Number of Gauss points (integration order) per sub-element.
        
    Returns
    -------
    sympy.Float or sympy.Matrix
        The numerical result of the integration.
    """
    a, b = float(x_range[0]), float(x_range[1])
    
    # 1. Get Reference Gauss Nodes/Weights for [-1, 1]
    xi_ref, w_ref = leggauss(points_per_interval)

    # 2. Generate Sub-intervals
    edges = np.linspace(a, b, n_intervals + 1)
    
    # 3. Map Nodes and Weights to Physical Domain [a, b]
    # We compute the Jacobian (half_width) and shift (mid_point) for every interval
    all_nodes = []
    all_weights = []
    
    for i in range(n_intervals):
        x_start, x_end = edges[i], edges[i+1]
        half_width = 0.5 * (x_end - x_start)
        mid_point = 0.5 * (x_end + x_start)
        
        # Map reference nodes [-1, 1] to physical [x_start, x_end]
        loc_nodes = mid_point + half_width * xi_ref
        loc_weights = half_width * w_ref # Scale weights by Jacobian
        
        all_nodes.append(loc_nodes)
        all_weights.append(loc_weights)

    # Flatten to single arrays for vectorized evaluation
    xi_global = np.concatenate(all_nodes)
    wi_global = np.concatenate(all_weights)

    # 4. Evaluate and Sum
    if isinstance(expr, list):
        expr = Matrix(expr)

    if isinstance(expr, Matrix):
        rows, cols = expr.shape
        result = Matrix.zeros(rows, cols)
        for i in range(rows):
            for j in range(cols):
                # Lambdify allows numpy array input for fast evaluation
                f = lambdify(x_sym, expr[i, j], 'numpy')
                vals = f(xi_global)
                # If expression is constant, lambdify might return a scalar, handle broadcasting
                if np.isscalar(vals): 
                    vals = np.full_like(xi_global, vals)
                result[i, j] = Float(np.sum(vals * wi_global))
        return result
    else:
        # Scalar Case
        f = lambdify(x_sym, expr, 'numpy')
        vals = f(xi_global)
        if np.isscalar(vals):
            vals = np.full_like(xi_global, vals)
        return Float(np.sum(vals * wi_global))