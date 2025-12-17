import sympy as sp
from sympy import Piecewise, simplify

def symbolic_BSpline(t, c=None, k=None, xi_symbol=None):
    """
    Symbolic B-Spline with explicit zero outside the knot vector domain.
    """
    if xi_symbol is None:
        xi_symbol = sp.Symbol('xi')

    K = list(t)
    n_basis = len(K) - k - 1
    if c is None:
        c = [1] * n_basis  # default all basis coefficients to 1

    # Recursive definition of basis function
    def N(i, p):
        if p == 0:
            # Right-closed for the last interval
            cond = (xi_symbol >= K[i]) & (xi_symbol < K[i+1])

            if K[i+1] == K[-1]:
                cond = (xi_symbol >= K[i]) & (xi_symbol <= K[i+1])
    
            return Piecewise((1, cond), (0, True))
        else:
            left_denom = K[i+p] - K[i]
            right_denom = K[i+p+1] - K[i+1]
            left_term = 0
            right_term = 0
            if left_denom != 0:
                left_term = (xi_symbol - K[i]) / left_denom * N(i, p-1)
            if right_denom != 0:
                right_term = (K[i+p+1] - xi_symbol) / right_denom * N(i+1, p-1)
            expr = simplify(left_term + right_term)

            # Restrict support to [K[i], K[i+p+1]]
            support_cond = (xi_symbol >= K[i]) & (xi_symbol <= K[i+p+1])
            return Piecewise((expr, support_cond), (0, True))

    # Build the spline as a weighted sum of basis functions
    spline_expr = sum(c[i] * N(i, k) for i in range(n_basis))

    # Final restriction: zero outside the full knot vector domain
    full_domain_cond = (xi_symbol >= K[0]) & (xi_symbol <= K[-1])
    spline_expr = Piecewise((spline_expr, full_domain_cond), (0, True))

    return simplify(spline_expr)
