# gf2-irreducibles 🔐

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/gf2-irreducibles.svg)](https://pypi.org/project/gf2-irreducibles/)

A zero-dependency, high-performance lookup library for **low-weight binary irreducible polynomials** over $GF(2)$.

This library contains a pre-computed database of polynomials for degrees $n$ where $2 \le n \le 10,000$. It is designed for researchers and engineers working in cryptography (ECC, finite field arithmetic) who need instant access to standard irreducible polynomials without expensive runtime testing.

## 🚀 Installation

```bash
pip install gf2-irreducibles
````

## 📖 Usage

### Basic Lookup

Retrieve the minimal weight polynomial for a given degree.

```python
import gf2_irreducibles as gf2

# Get the polynomial for degree 8
poly = gf2.get_poly(8)

print(f"Polynomial: {poly}")
# Output: x^8 + x^4 + x^3 + x^1 + 1

print(f"Integer:    {poly.to_int()}")
# Output: 283  (useful for bitwise operations)

print(f"Hex:        {poly.to_hex()}")
# Output: 0x11b
```

### Checking Availability

```python
if gf2.has_degree(123):
    print("Polynomial found!")
```

### LaTeX Output for Papers

Useful for copying formulas directly into academic papers or reports.

```python
# Generate LaTeX string for documentation
print(poly.to_latex())
# Output: x^{8} + x^{4} + x^{3} + x + 1
```

## 📚 Data Source

The polynomial data is derived from the technical report:

> **"Table of Low-Weight Binary Irreducible Polynomials"** \> *Gadiel Seroussi* \> Hewlett-Packard Systems Laboratory, Report HPL-98-135, August 1998.

This library implements the data tables presented in the report, providing:

  * [cite_start]**Trinomials** ($x^n + x^k + 1$) where they exist[cite: 27].
  * [cite_start]**Pentanomials** ($x^n + x^{k_1} + x^{k_2} + x^{k_3} + 1$) where trinomials do not exist[cite: 28].

[cite_start]Among those of minimum weight, the polynomial listed is the one where the intermediate degrees are lowest (lexicographically first)[cite: 11].

## ⚡ Performance

  * **O(1) Lookup:** Uses a static hash map. No irreducibility tests are performed at runtime.
  * **Zero Dependencies:** Pure Python, standard library only.
  * **Lightweight:** Minimal memory footprint.

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)