from sympy.physics import units
from sympy.physics.units.prefixes import prefix_unit, PREFIXES

prefixable_units = [
            units.henry,
            units.lux,
            units.pascal,
            units.candela,
            units.kelvin,
            units.farad,
            units.katal,
            units.hertz,
            units.ohm,
            units.joule,
            units.volt,
            units.becquerel,
            units.watt,
            units.ampere,
            units.second,
            units.siemens,
            units.gray,
            units.tesla,
            units.weber,
            units.meter,
            units.gram,
            units.newton,
            units.coulomb,
            units.mol,
            units.bit,
            units.byte,
            units.liter,
            units.mole
            ]

# Set the abbreviations for bit and byte
units.bit._abbrev = "b"
units.byte._abbrev = "B"

# Run through all prefixable units and create prefixed versions
for unit in prefixable_units:
    for prefixed_unit in prefix_unit(unit, PREFIXES): # go through all prefixes

        # Create a prefixed unit with the same latex properties as the original unit
        if unit._latex_repr or "micro" in prefixed_unit.name.__str__():
            latex_repr = r"\mathrm{%s}" % prefixed_unit.abbrev.__str__()
            
        # Replace the unit name in the LaTeX representation with the prefixed unit's LaTeX representation
            latex_repr = latex_repr.replace(unit.name.__str__(),str(unit._latex_repr))

        # If the unit is a micro unit, replace 'mu' with LaTeX representation for micro
            latex_repr = latex_repr.replace("mu", r"\mu ") 

            prefixed_unit._latex_repr = latex_repr  
        
        # Update sympy original unit package attributes with the prefixed unit
        setattr(units, prefixed_unit.name.__str__(), prefixed_unit)
        setattr(units, prefixed_unit.abbrev.__str__(), prefixed_unit)