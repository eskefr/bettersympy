from sympy.printing.latex import LatexPrinter, _between_two_numbers_p
from sympy import Mul, Pow, S, Number
from sympy.physics.units import Quantity
from sympy.core.expr import Expr
#from sympy.simplify import fraction
from sympy.utilities import sift


class CustomLatexPrinter(LatexPrinter):
    
    def _print_Mul(self, expr: Expr):    
        from sympy.simplify import fraction
        separator: str = self._settings['mul_symbol_latex']
        numbersep: str = self._settings['mul_symbol_latex_numbers']
        unit_tex = ""
        unit_check = True
        
        if all(isinstance(arg, Quantity) or (isinstance(arg, Pow) and isinstance(arg.base, Quantity)) for arg in expr.args):
            unit_check = False
        elif unit_check and any(isinstance(arg, Quantity) or (isinstance(arg, Pow) and isinstance(arg.base, Quantity)) for arg in expr.args):
            unit = S.One
            for arg in expr.args:
                if isinstance(arg, Quantity) or (isinstance(arg, Pow) and isinstance(arg.base, Quantity)):
                    unit *= arg
            
            unit_tex = self._print_Mul(unit)
            expr = expr / unit
            print(unit_tex,expr,unit)
        


        def convert(expr) -> str:
            if not expr.is_Mul:
                return str(self._print(expr))
            else:
                if self.order not in ('old', 'none'):
                    args = expr.as_ordered_factors()
                else:
                    args = list(expr.args)

                # If there are quantities or prefixes, append them at the back.
                units, nonunits = sift(args, lambda x: (isinstance(x, Quantity) or (isinstance(x, Pow) and isinstance(x.base, Quantity))) or (hasattr(x, "_scale_factor") or hasattr(x, "is_physical_constant")), binary=True)
                prefixes, units = sift(units, lambda x: hasattr(x, "_scale_factor"), binary=True)

                return convert_args(nonunits + prefixes + units)

        def convert_args(args) -> str:
            _tex = last_term_tex = ""

            for i, term in enumerate(args):
                term_tex = self._print(term)
                if not (hasattr(term, "_scale_factor") or hasattr(term, "is_physical_constant")):
                    if self._needs_mul_brackets(term, first=(i == 0),
                                                last=(i == len(args) - 1)):
                        term_tex = r"\left(%s\right)" % term_tex

                    if  _between_two_numbers_p[0].search(last_term_tex) and \
                        _between_two_numbers_p[1].match(term_tex):
                        # between two numbers
                        _tex += numbersep
                    elif _tex:
                        _tex += separator
                elif _tex:
                    _tex += separator

                _tex += term_tex
                last_term_tex = term_tex
            return _tex

        # Check for unevaluated Mul. In this case we need to make sure the
        # identities are visible, multiple Rational factors are not combined
        # etc so we display in a straight-forward form that fully preserves all
        # args and their order.
        # XXX: _print_Pow calls this routine with instances of Pow...
        if isinstance(expr, Mul):
            args = expr.args
            
            if args[0] is S.One or any(isinstance(arg, Number) for arg in args[1:]):
                return convert_args(args)

        include_parens = False
        if expr.could_extract_minus_sign():
            expr = -expr
            tex = "- "
            if expr.is_Add:
                tex += "("
                include_parens = True
        else:
            tex = ""

        numer, denom = fraction(expr, exact=True)

        if denom is S.One and Pow(1, -1, evaluate=False) not in expr.args:
            # use the original expression here, since fraction() may have
            # altered it when producing numer and denom
            tex += convert(expr)
            tex += unit_tex

        else:
            snumer = convert(numer)
            snumer += unit_tex
            sdenom = convert(denom)
            ldenom = len(sdenom.split())
            ratio = self._settings['long_frac_ratio']
            if self._settings['fold_short_frac'] and ldenom <= 2 and \
                    "^" not in sdenom:
                # handle short fractions
                if self._needs_mul_brackets(numer, last=False):
                    tex += r"\left(%s\right) / %s" % (snumer, sdenom)
                else:
                    tex += r"%s / %s" % (snumer, sdenom)
            elif ratio is not None and \
                    len(snumer.split()) > ratio*ldenom:
                # handle long fractions
                if self._needs_mul_brackets(numer, last=True):
                    tex += r"\frac{1}{%s}%s\left(%s\right)" \
                        % (sdenom, separator, snumer)
                elif numer.is_Mul:
                    # split a long numerator
                    a = S.One
                    b = S.One
                    for x in numer.args:
                        if self._needs_mul_brackets(x, last=False) or \
                                len(convert(a*x).split()) > ratio*ldenom or \
                                (b.is_commutative is x.is_commutative is False):
                            b *= x
                        else:
                            a *= x
                    if self._needs_mul_brackets(b, last=True):
                        tex += r"\frac{%s}{%s}%s\left(%s\right)" \
                            % (convert(a), sdenom, separator, convert(b))
                    else:
                        tex += r"\frac{%s}{%s}%s%s" \
                            % (convert(a), sdenom, separator, convert(b))
                else:
                    tex += r"\frac{1}{%s}%s%s" % (sdenom, separator, snumer)
            else:
                tex += r"\frac{%s}{%s}" % (snumer, sdenom)

        if include_parens:
            tex += ")"
        return tex

LatexPrinter._print_Mul = CustomLatexPrinter._print_Mul
