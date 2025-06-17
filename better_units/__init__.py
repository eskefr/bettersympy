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

from IPython.display import display, Markdown
display(Markdown("""
## BetterSympy Usage Guide

This package provides enhanced functionality for using units in SymPy.

### Key Components:

*   **`units` (or `u`)**:  A dictionary containing predefined physical units.  Access units like `u.meter`, `u.second`, etc.

*   **`plot(*args, **kwargs)`**:  An enhanced plotting function that automatically handles units and adds them to axis labels.

*   **`s`**:  A shortcut for SymPy's `abc` module, providing common symbols like `s.x`, `s.y`, `s.t`, etc.

### Examples:

#### Define Unit Expression:

```python
# Define a quantity with units
velocity = 10 * units.meter / units.seconds # or faster: 10*u.m/u.s

# Adding acceleration depinding on velocity time
velocity = velocity + 2 * u.m / u.s**2 * s.t
                 
# Plotting with Units:
plot(velocity, (s.t, 0, 10*u.s), title="Velocity over Time") 
                 
distance = integrate(velocity)
plot(distance,(s.t,0,10*u.s), title="Distance over Time")
        """))

# Export the main components
__all__ = ['units', 'plot', 'u', 's'] + sympy_all