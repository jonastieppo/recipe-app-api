"""
Sample tests 
"""

from django.test import SimpleTestCase

from app import calc

class CalcTests(SimpleTestCase):

    def test_add_numbers(self):
        """ Tests the calc function from calc module """
        res = calc.add(5,6)

        self.assertEqual(res, 11)

    def test_subtract_numbers(self):
        """ Tests the subtraction of numbers """

        res = calc.subtract(5,11)

        self.assertEqual(res, -6)

    