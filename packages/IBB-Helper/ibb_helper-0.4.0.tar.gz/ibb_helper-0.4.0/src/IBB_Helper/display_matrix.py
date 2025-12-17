import numpy                as     np
import sympy                as     sp
from   sympy                import latex
from   IPython.display      import Math, display

def display_matrix(matrix, name="Matrix", r=8, c=8, evalf=False, prec=5):
    """
    Displays a truncated matrix with optional numerical evaluation and rational simplification.
    
    Parameters:
        matrix  : Input matrix (NumPy array, SymPy Matrix, or list)
        name    : Display name (default: "Matrix")
        r       : Max rows to display (default: 8)
        c       : Max columns to display (default: 8)
        evalf   : If T, apply numerical evaluation (default: F)
        prec    : Evaluate the given formula to an accuracy of prec digits
    """
    
    # Convert to SymPy Matrix if needed
    if isinstance(matrix, (np.ndarray, list)):
        matrix = sp.Matrix(matrix)

    # Truncate to r rows and c columns
    submatrix = matrix[:min(r, matrix.rows), :min(c, matrix.cols)]

    # Apply evaluation if needed
    if evalf:
        processed = submatrix.applyfunc(lambda x: x.evalf(prec))
    else:
        processed = submatrix

    # Display matrix
    display(Math(f"{name} = {latex(processed)}"))

    m = matrix.rows
    n = matrix.cols
    # Show truncation message if applicable
    if matrix.rows > r or matrix.cols > c:
        display(Math(rf"\text{{... Truncated to first {r}x{c} out of {m}x{n} matrix}}"))