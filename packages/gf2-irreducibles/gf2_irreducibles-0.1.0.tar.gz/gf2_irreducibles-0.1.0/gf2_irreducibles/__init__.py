from .polys import POLY_DICT

class IrreduciblePoly:
    def __init__(self, degree, middle_terms):
        self.degree = degree
        # The document implies all polys include x^n and 1 [cite: 34, 35]
        self.middle_terms = sorted(middle_terms, reverse=True)
        self.all_exponents = self.middle_terms

    def __repr__(self):
        """Returns a mathematical string representation."""
        terms = [f"x^{e}" if e > 0 else "1" for e in self.all_exponents]
        return " + ".join(terms)

    def to_tuple(self):
        """Returns tuple of exponents, e.g., (5, 2, 0)"""
        return tuple(self.all_exponents)

    def to_int(self):
        """Returns the integer representation (bitmask)."""
        res = 0
        for e in self.all_exponents:
            res |= (1 << e)
        return res

    def to_hex(self):
        """Returns hex string of the polynomial."""
        return hex(self.to_int())

def get_poly(n: int) -> IrreduciblePoly:
    """
    Retrieve the minimal weight irreducible polynomial for degree n.
    Source: Gadiel Seroussi, HPL-98-135[cite: 3].
    """
    if n not in POLY_DICT:
        raise ValueError(f"Polynomial for degree {n} not found in database.")
    
    return IrreduciblePoly(n, POLY_DICT[n])

def has_degree(n: int) -> bool:
    """Check if degree n is available in the library."""
    return n in POLY_DICT

if __name__ == "__main__":
    import sys
    try:
        degree = int(sys.argv[1])
        print(get_poly(degree))
    except (IndexError, ValueError):
        print("Usage: python -m gf2_irreducibles <degree>")