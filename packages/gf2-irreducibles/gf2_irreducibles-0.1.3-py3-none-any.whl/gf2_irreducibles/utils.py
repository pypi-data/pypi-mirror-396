def to_latex(middle_terms: list) -> str:
    """
    Converts polynomial terms to a LaTeX string.
    
    Args:
        degree (int): The degree of the polynomial.
        middle_terms (list): The exponents of the middle terms.
        
    Returns:
        str: LaTeX formatted string, e.g., "x^{5} + x^{2} + 1"
    """
    # Sort terms: degree -> middle terms (descending) -> 0
    exponents = sorted(middle_terms, reverse=True)
    
    terms = []
    for e in exponents:
        if e == 0:
            terms.append("1")
        elif e == 1:
            terms.append("x")
        else:
            terms.append(f"x^{{{e}}}")
            
    return " + ".join(terms)

def validate_degree(n: int):
    """
    Simple validator to ensure the degree is a positive integer.
    """
    if not isinstance(n, int):
        raise TypeError(f"Degree must be an integer, got {type(n).__name__}")
    if n < 2:
        raise ValueError("Degree must be at least 2.")