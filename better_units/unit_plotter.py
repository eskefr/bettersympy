from sympy import *
from sympy.plotting import plot
from sympy.physics.units import Quantity

## We have to be able to plot like this ##

f = 2*symbols('x') + 3

#plot(f, (symbols('x'), -10, 10), xlabel='x', ylabel='f(x)', show=True)

## But for a scenario with units ##
from units_definition import units as u
import unit_printer

f = 2*u.kPa/u.s *symbols('x') + 3 * u.kPa # where x is in seconds

def unit_splitter(expr):
    """
    Splits the expression into its unit and non-unit parts.
    """
    # Split the multiplication into unit and non-unit parts.
    nonunit = unit = S.One
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
        
        return adds, units

def find_x_and_y_unit(units: list):
    """
    Finds the unit of x in the list of units.
    """
    return units[0]/units[1], units[0]
        
def unit_plot(expr, x_range, xlabel='x', ylabel='y', show=True):
    """
    Plots the expression with units.
    """
    nonunit, unit = unit_splitter(expr)
    
    # Find the unit of x and y
    x_unit, y_unit = find_x_and_y_unit(unit)
    plot(nonunit, xlabel=xlabel+f" [{x_unit}]", ylabel=ylabel+f" [{y_unit}]", show=show)
    
#plot(unit_splitter(f), (symbols('x'), 0, 10*u.s), xlabel='Time (s)', ylabel='Pressure (kPa)', show=True)