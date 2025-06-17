from sympy import *
#from sympy.core.basic import Basic
from sympy.physics.units import Quantity

def remove_unit(expr: Expr, scale: bool = True) -> Expr:
    """
    Removes the units from the expression.
    Parameters
    ----------
    expr : Expr
        The expression from which to remove the units.
    scale : bool, optional
        If True, scales the expression by the scale factor of the units. If False, sets the units to 1.
    Returns
    -------
    Expr
        The expression with units removed.
    """
    units = expr.atoms(Quantity)
    for unit in units:
        expr = expr.subs(unit, unit.scale_factor if scale else 1)
    return expr

def find_unit(expr,x_unit):
    """
    Finds the unit of the expression by splitting it into unit and non-unit parts.
    Parameters
    ----------
    expr : Expr
        The expression to analyze.
    x_unit : Quantity
        The unit of the variable x.
    Returns
    -------
    unit : Quantity
        The unit of the expression.
    """
    # Split the multiplication into unit and non-unit parts.
    unit = None
    if len(expr.free_symbols) != 1:
        raise ValueError("The expression must contain only one variable.")
    else:
        var = expr.free_symbols.pop()
        unit = expr.subs(var, x_unit).as_coeff_Mul()[1]
    
    return unit

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

    expr = unit_x = unit_y = None

    args = list(args)
    for i, a in enumerate(args):
        a = sympify(a)
        if isinstance(a, (list, Tuple)):
            if a[-1].atoms(Quantity):
                unit_x = a[-1].as_coeff_Mul()[1]
                unit_y = find_unit(expr, unit_x)
                print(unit_x, unit_y)
            ran, _ = _plot_sympify(a)
            args[i] = Tuple(*ran, sympify=False)
        elif a.atoms(Quantity):
            expr = a
            args[i] = remove_unit(a, scale=False)
        elif not (
            isinstance(a, (str, dict)) or callable(a)
            or (
                (a.__class__.__name__ == "Vector") and
                not isinstance(a, Basic)
            )
        ):
            args[i] = a
    return args, (unit_x, unit_y)


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

    **kwargs : dict
        Additional keyword arguments for the plot function.
    
    Returns
    -------
    Plot object
        The plot object containing the plotted expression.
    """
    args, units = _plot_sympify(args)
    print("Units found:", units)
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
    kwargs["xlabel"] = str(kwargs["xlabel"]) + r" $\left[%s\right]$" % latex(units[0]).replace(r"\text",r"\,\operatorname") if units[0] else ""
    kwargs["ylabel"] = str(kwargs["ylabel"]) + r" $\left[{%s}\right]$" % latex(units[1]).replace(r"\text",r"\,\operatorname") if units[1] else ""

    gs = _create_generic_data_series(**kwargs)
    return graphics(*lines, gs, **kwargs)