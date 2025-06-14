# __init__.py
from sympy import *
from sympy import abc as s
from .units_definition import units
from .units_definition import units as u
from .unit_printer import CustomLatexPrinter
from sympy.printing.latex import LatexPrinter
from .unit_plot import plot

from sympy import __all__ as sympy_all

# Apply the custom printer globally
LatexPrinter._print_Mul = CustomLatexPrinter._print_Mul

# Export the main components
__all__ = ['units', 'plot', 'u', 's'] + sympy_all