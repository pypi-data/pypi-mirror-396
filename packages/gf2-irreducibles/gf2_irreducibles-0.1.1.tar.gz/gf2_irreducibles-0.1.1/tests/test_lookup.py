import unittest
from gf2_irreducibles import get_poly, has_degree

class TestIrreducibles(unittest.TestCase):

    def test_trinomial_lookup(self):
        # Case from HPL-98-135, Page 4: n=3, middle=1 -> x^3 + x + 1
        poly = get_poly(3)
        self.assertEqual(poly.degree, 3)
        self.assertEqual(tuple(poly.middle_terms), (1,))
        self.assertEqual(poly.to_int(), (1<<3) | (1<<1) | 1) # 1011 binary = 11

    def test_pentanomial_lookup(self):
        # Case from HPL-98-135, Page 4: n=8, middle=4,3,1 -> x^8 + x^4 + x^3 + x + 1
        poly = get_poly(8)
        self.assertEqual(poly.degree, 8)
        self.assertEqual(tuple(poly.middle_terms), (4, 3, 1))
        
        # Check integer representation
        # 1 0001 1011 = 256 + 16 + 8 + 2 + 1 = 283
        expected_int = (1<<8) | (1<<4) | (1<<3) | (1<<1) | 1
        self.assertEqual(poly.to_int(), expected_int)

    def test_high_degree_lookup(self):
        # Check edge case if you have it in your dict, e.g., n=10000
        # From source text: n=10,000 is pentanomial
        if has_degree(10000):
            poly = get_poly(10000)
            self.assertEqual(poly.degree, 10000)
            # Ensure it has exactly 3 middle terms (pentanomial)
            self.assertEqual(len(poly.middle_terms), 3)

    def test_invalid_lookup(self):
        with self.assertRaises(ValueError):
            get_poly(999999)  # Something not in the table

if __name__ == '__main__':
    unittest.main()