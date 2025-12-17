import numpy                as     np
import sympy                as     sp
from   sympy                import latex
import IPython.display      as     ipy

def display_eigen(A, name="Matrix", evalf=False, prec=5, return_data=False, show="both", output="default"):
    """
    Computes and displays the eigenvalues and eigenvectors of a matrix A with enhanced display options.

    Parameters:
        A          : Square matrix (SymPy Matrix or NumPy ndarray)
        name       : Label used for the matrix (default="Matrix")
        evalf      : If True, show decimal values (default=False)
        prec       : Evaluate the given formula to an accuracy of prec digits (default: 5)
        show       : What to display ("both", "eigvals", "eigvecs", or "none") (default="both")
        output     : How to display ("default", "compact", "Maple") (default="default")
        return_data: If True, also returns eigenvalues and eigenvectors (default=False)

    Returns (if return_data=True):
        - eigvals: List of eigenvalues
        - eigvecs: List of corresponding eigenvectors (each as a SymPy Matrix)
    """

    threshold = 10**(-10)

    def safe_eval(x):
        try:
            val = x.evalf(prec)
            if abs(val) < threshold:
                return sp.Integer(0)
            return round(float(val), prec)
        except (TypeError, ValueError):
            return x

    # Convert NumPy array to SymPy Matrix if needed
    if isinstance(A, np.ndarray):
        A = sp.Matrix(A)

    # Compute eigenvalues and eigenvectors
    eigen_data = A.eigenvects()

    # To store raw data
    eigvals = []
    eigvecs = []

    # Validate show parameter
    show = show.lower()
    valid_options = ["both", "eigvals", "eigvecs", "none"]
    if show not in valid_options:
        raise ValueError(f"show must be one of {valid_options}")

    # Validate output parameter
    output = output.lower()
    valid_options_output = ["default", "compact", "maple"]
    if output not in valid_options_output:
        raise ValueError(f"output must be one of {valid_options_output}")


    # Prepare data
    counter = 1
    for eigval, mult, vects in eigen_data:
        for i in range(mult):
            val_disp = safe_eval(eigval) if evalf else eigval
            v_disp = vects[i].applyfunc(safe_eval) if evalf else vects[i]
            eigvals.append(val_disp)
            eigvecs.append(v_disp)
            counter += 1


    # Build LaTeX string based on options
    if show == "both":
        latex_str = f"\\text{{Eigenvalues and Eigenvectors of }} {name}:"
        ipy.display(ipy.Math(latex_str))
        if output == "default":
            latex_str = f""
            for i, (val, vec) in enumerate(zip(eigvals, eigvecs)):
                latex_str += f"\\lambda_{{{i+1}}} = {latex(val)}, v_{{{i+1}}} = {latex(vec)} \\qquad"
            ipy.display(ipy.Math(latex_str))
        elif output == "compact":
            for i, (val, vec) in enumerate(zip(eigvals, eigvecs)):
                latex_str = f"\\lambda_{{{i+1}}} = {latex(val)}, \\quad v_{{{i+1}}} = {latex(vec.T)}"
                ipy.display(ipy.Math(latex_str))
        elif output == "maple":
            latex_str = f"\\lambda = {latex(sp.Matrix(eigvals))}"
            ipy.display(ipy.Math(latex_str))
            V = sp.Matrix.hstack(*[vec for vec in eigvecs])
            latex_str = f"v = {latex(V)}"
            ipy.display(ipy.Math(latex_str))

    elif show == "eigvals":
        # Default vector display for eigenvalues only
        latex_str = f"\\text{{Eigenvalues of }} {name}: \\quad \\lambda = {latex(sp.Matrix(eigvals))}"
        ipy.display(ipy.Math(latex_str))

    elif show == "eigvecs":
        # Default matrix display for eigenvectors only
        V = sp.Matrix.hstack(*[vec for vec in eigvecs])
        latex_str = f"\\text{{Eigenvectors of }} {name}: \\quad v = {latex(V)}"
        ipy.display(ipy.Math(latex_str))


    if return_data:
        return eigvals, eigvecs
    return None
