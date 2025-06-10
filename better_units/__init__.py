# __init__.py
from sympy import *
from .units_definition import units
from .units_definition import units as u
from .unit_printer import CustomLatexPrinter
from sympy.printing.latex import LatexPrinter


# Apply the custom printer globally
LatexPrinter._print_Mul = CustomLatexPrinter._print_Mul

# Export the main components
__all__ = ['units', 'CustomLatexPrinter', 'custom_latex']