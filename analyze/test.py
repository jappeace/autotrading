"""
Executes unit tests
"""
import unittest
from lib import rate


class TestRating(unittest.TestCase):

    def test_anuity_valuation_happy_path(self):
        data = reversed(['2.75', '1.05', '2.28', '4.27', '2.89', '2.1', '2.59', '0.35', '-1.2', '1.1'])
        self.assertEqual(
            round(rate.valuate_anuity(data), 2),
            10.57-1.43 # google sheets test case
        )

    def test_anuity_missing_data(self):
        self.assertEqual(
            rate.valuate_anuity(['2.75', '', '2.28']),
            None
        )
        self.assertEqual(
            rate.valuate_anuity(['']),
            None
        )
        self.assertEqual(
            rate.valuate_anuity(['', '2.2']),
            None
        )

if __name__ == '__main__':
    unittest.main()
