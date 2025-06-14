from sympy import *
from sympy.core.basic import Basic
from sympy.physics.units import Quantity
from sympy.plotting import plot
from sympy.plotting.plot import Plot
from sympy.plotting.plot import _check_arguments, _build_line_series, _set_labels, plot_factory
import matplotlib.pyplot as plt 

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

documentation_string = plot.__doc__
def plot(*args, show=True, **kwargs):
    __doc__ = documentation_string # temporary fix for sphinx documentation
    
    args, units = _plot_sympify(args)
            
    plot_expr = _check_arguments(args, 1, 1, **kwargs)
    params = kwargs.get("params", None)
    free = set()
    for p in plot_expr:
        if not isinstance(p[1][0], str):
            free |= {p[1][0]}
        else:
            free |= {Symbol(p[1][0])}
    if params:
        free = free.difference(params.keys())
    x = free.pop() if free else Symbol("x")
    kwargs.setdefault('xlabel', x)
    kwargs.setdefault('ylabel', Function('f')(x))
    labels = kwargs.pop("label", [])
    rendering_kw = kwargs.pop("rendering_kw", None)
    series = _build_line_series(*plot_expr, **kwargs)
    _set_labels(series, labels, rendering_kw)

    plots = plot_factory(*series, **kwargs)

    if units[0] is not None:
        plots.xlabel = str(plots.xlabel) + fr" $\left[{latex(units[0])}\right]$"
        plots.ylabel = str(plots.ylabel) + fr" $\left[{latex(units[1])}\right]$"

    if show:
        plots.show()
    return plots