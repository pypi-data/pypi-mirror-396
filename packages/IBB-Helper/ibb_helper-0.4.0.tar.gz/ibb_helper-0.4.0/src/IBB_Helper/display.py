import numpy                as     np
import sympy                as     sp
from   sympy                import latex
import IPython.display      as     ipy

def display(obj, name="obj", evalf=False, prec=5):
    """
    Converts vectors/numbers/matrices to LaTeX with optional simplification.

    Parameters:
        obj     : Input (SymPy or NumPy object)
        name    : Name used for display
        evalf   : If T, evaluates to decimal form before display (default: F)
        prec    : Evaluate the given formula to an accuracy of prec digits (default: 5)
    """

    def safe_eval_entry(x):
        try:
            return sp.sympify(x).evalf(prec)
        except (TypeError, ValueError):
            return x

    if evalf:
        if isinstance(obj, np.ndarray):
            obj = sp.Matrix(obj).applyfunc(safe_eval_entry)
        elif isinstance(obj, (sp.Matrix, list)):
            obj = sp.Matrix(obj).applyfunc(safe_eval_entry)
        elif isinstance(obj, sp.NDimArray):
            obj = obj.applyfunc(safe_eval_entry)
        else:
            obj = safe_eval_entry(obj)
    else:
        if isinstance(obj, np.ndarray):
            obj = sp.Matrix(obj)
        elif isinstance(obj, (sp.Matrix, list)):
            obj = sp.Matrix(obj)
        elif isinstance(obj, sp.NDimArray):
            obj = obj
        else:
            obj = sp.sympify(obj)

    ipy.display(ipy.Math(f"{name} = {latex(obj)}"))