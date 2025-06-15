from sympy import *
from sympy.core.basic import Basic
from sympy.physics.units import Quantity

def unit_splitter(expr):
    """
    Splits the expression into its unit and non-unit parts.
    """
    # Split the multiplication into unit and non-unit parts.
    nonunit = unit = S.One
    if isinstance(expr, Number):
        # If the expression is a number, return it self.
        return expr, [unit]
    
    if isinstance(expr, Mul):
        for arg in expr.args:
            if isinstance(arg, Quantity) or (isinstance(arg, Pow) and isinstance(arg.base, Quantity)):
                unit *= arg
            else:
                nonunit *= arg
        return nonunit, [unit]
    
    # If the expression is an addition, we need to handle it iterativly.
    if isinstance(expr, Add):
        units = []
        adds = S.Zero
        for mul in expr.args:
            nu, u = unit_splitter(mul)
            adds += nu
            units += u
        #
        if not adds.is_Add:
            print("Warning: The number of units does not match the number of terms in the addition. This may lead to incorrect results.")
        # Make sure the first unit is unit foctor of x by reversing the order if the second unit has free symbols.
        units = units[::-1] if expr.args[1].free_symbols else units
        return adds, units

def find_x_unit(expr):
    """
    Finds the unit of x in the expression.
    """
    # since the intercept term will always have the true unit of y, the term with x equal to the intercept term will yield the unit of x.
    sol = solve(Eq(*expr.args))[0]
    if isinstance(sol, (Pow, Quantity)):
        return sol
    else:
        return unit_splitter(sol)[1][0]
    
def find_y_unit(expr, x_unit):
    """
    Finds the unit of y in the expression.
    """
    # since the intercept term will always have the true unit of y, the term with x equal to zero will yield the unit of y.
    sol = expr.subs(expr.free_symbols.pop(), x_unit)
    if isinstance(sol, (Pow, Quantity)):
        return sol
    else:
        return unit_splitter(sol)[1][0]


def _plot_sympify(args):
    """This function recursively loop over the arguments passed to the plot
    functions: the sympify function will be applied to all arguments except
    those of type string/dict.

    Generally, users can provide the following arguments to a plot function:

    expr, range1 [tuple, opt], ..., label [str, opt], rendering_kw [dict, opt]

    `expr, range1, ...` can be sympified, whereas `label, rendering_kw` can't.
    In particular, whenever a special character like $, {, }, ... is used in
    the `label`, sympify will raise an error.
    """
    if isinstance(args, Expr):
        return args

    x_unit = y_unit = None
    
    args = list(args)
    expr = None
    for i, a in enumerate(args):
        if isinstance(a, (list, tuple)):
            nonunit = _plot_sympify(a)[0]
            args[i] = Tuple(*nonunit, sympify=False)

            a = sympify(a[-1])

            if isinstance(a, Number):
                continue
            else:
                if isinstance(a, (Pow, Quantity)):
                    unit = a
                else:
                    unit = unit_splitter(a)[1][0]
                
                # This input will set the x range so the units will be x, just take the first unit.
                x_unit = unit
                y_unit = find_y_unit(expr,x_unit)

        elif isinstance(a, (Mul, Add)):
            nonunit, unit  = unit_splitter(a)
            expr = a
            args[i] = nonunit
            if unit != [1,1]:
                if len(unit) > 2:
                    raise ValueError("The expression contains too many units, which is not supported.")
                elif len(unit) == 2:
                    # If we have two units, the second is forced to be y unit from unit_splitter.
                    y_unit = unit[1]
                    # find what x needs to be multiplied with to get y.
                    x_unit = find_x_unit(a)

            
        elif not (isinstance(a, (str, dict)) or callable(a)
            # NOTE: check if it is a vector from sympy.physics.vector module
            # without importing the module (because it slows down SymPy's
            # import process and triggers SymPy's optional-dependencies
            # tests to fail).
            or ((a.__class__.__name__ == "Vector") and not isinstance(a, Basic))
        ):
            args[i] = sympify(a)
    return args, [x_unit, y_unit]


from spb.defaults import TWO_D_B
from spb.graphics import graphics, line
from spb.utils import _check_arguments
from spb.plot_functions.functions_2d import _create_generic_data_series, _set_labels

def plot(*args, **kwargs):
    """
    Plot the given expression with units.
    
    Parameters
    ----------
    *args : list
        The expression to plot and the range of x.
    show : bool, optional
        Whether to show the plot or not. Default is True.
    **kwargs : dict
        Additional keyword arguments for the plot function.
    
    Returns
    -------
    Plot object
        The plot object containing the plotted expression.
    """
    args, units = _plot_sympify(args)
    plot_expr = _check_arguments(args, 1, 1, **kwargs)
    global_labels = kwargs.pop("label", [])
    global_rendering_kw = kwargs.pop("rendering_kw", None)
    lines = []
    for pe in plot_expr:
        expr, r, label, rendering_kw = pe
        lines.extend(line(expr, r, label, rendering_kw, **kwargs))
    
    _set_labels(lines, global_labels, global_rendering_kw)
    kwargs.setdefault('xlabel', r"$x$")
    kwargs.setdefault('ylabel', r"$f(x)$")
    kwargs["xlabel"] = str(kwargs["xlabel"]) + r" $\left[\,%s\right]$" % latex(units[0]).replace(r"\text",r"\operatorname") if units[0] else ""
    kwargs["ylabel"] = str(kwargs["ylabel"]) + r" $\left[\,{%s}\right]$" % latex(units[1]).replace(r"\text",r"\operatorname") if units[1] else ""
    print(kwargs)
    gs = _create_generic_data_series(**kwargs)
    return graphics(*lines, gs, **kwargs)