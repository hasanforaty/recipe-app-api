from django.test import SimpleTestCase
from app.app import calc


class CalcTests(SimpleTestCase):
    def test_add_numbers(self):
        """Test adding two numbers"""
        self.assertEqual(calc.add(3, 8), 11)

    def test_subtract_numbers(self):
        """Test subtracting two numbers"""
        self.assertEqual(calc.subtract(8, 3), 5)
