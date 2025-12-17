import numpy as np
import scipy as sc
from sympy import symbols, lambdify, Eq, solve

# --- Minimize Function ---
def minimize(objective_func, opt_vars_list, constraints_dict, x0_initial_guess=None):
    """
    General purpose optimization wrapper that accepts symbolic expressions and constraints.

    Args:
        objective_func (sympy expression): The function (e.g., Delta) to minimize.
        opt_vars_list (list): The list of ALL symbolic variables being optimized (e.g., [X0, X1, ..., Y0, Y1, ...]).
        constraints_dict (dict): Constraints in the format {symbolic_variable: fixed_value}.
        x0_initial_guess (np.array, optional): Initial guess vector. Defaults to all zeros.

    Returns:
        OptimizeResult: The result object from scipy.optimize.minimize.
    """
    
    # 1. Separate optimization variables into free and constrained
    constrained_vars = list(constraints_dict.keys())
    fixed_values = np.array(list(constraints_dict.values()))
    
    # 2. Prepare Objective Function (takes ALL opt_vars_list)
    objective_func_raw = lambdify(opt_vars_list, objective_func, 'numpy')
    
    def objective_wrapper(x_flat):
        return objective_func_raw(*x_flat)

    # 3. Prepare Constraints for SciPy
    scipy_constraints = []
    
    # Find the index of each constrained variable in the flattened opt_vars_list
    for i, var in enumerate(opt_vars_list):
        if var in constrained_vars:
            # The constraint is: var - fixed_value = 0
            fixed_value = constraints_dict[var]
            
            def constraint_fun(x, index=i, val=fixed_value):
                # x[index] is the variable, val is the fixed boundary value
                return x[index] - val

            scipy_constraints.append({
                'type': 'eq', 
                'fun': constraint_fun
            })

    # 4. Prepare Initial Guess (start close to the constraints)
    num_vars = len(opt_vars_list)
    x0 = np.zeros(num_vars) if x0_initial_guess is None else x0_initial_guess.copy()
    
    # Set the initial guess to satisfy the constraints
    for var, val in constraints_dict.items():
        try:
            index = opt_vars_list.index(var)
            x0[index] = val
        except ValueError:
            pass # Variable not in optimization list
            
    # 5. Solve
    sol = sc.minimize(objective_wrapper, x0, constraints=scipy_constraints, method='SLSQP')
    return sol