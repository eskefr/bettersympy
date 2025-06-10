from sympy import *
from sympy.plotting import plot
from sympy.physics.units import Quantity

## We have to be able to plot like this ##

f = 2*symbols('x') + 3

plot(f, (symbols('x'), -10, 10), xlabel='x', ylabel='f(x)', show=True)

## But for a scenario with units ##
from units_definition import units as u
import unit_printer


f = 2*u.kPa/u.s *symbols('x') + 3 * u.kPa # where x is in seconds

def unit_splitter(expr):
    """
    Splits the expression into its unit and non-unit parts.
    """
    expr
    number = nonunit = unit = S.One
    for arg in expr.args:
        if isinstance(arg, Quantity) or (isinstance(arg, Pow) and isinstance(arg.base, Quantity)):
            unit *= arg
        elif isinstance(arg, Number):
            number *= arg
        else:
            nonunit *= arg
    return number, nonunit, unit

#plot(f, (symbols('x'), 0, 10*u.s), xlabel='Time (s)', ylabel='Pressure (kPa)', show=True)