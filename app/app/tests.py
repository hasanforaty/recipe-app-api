from django.test import SimpleTestCase
from app import calc
from django.urls import reverse
from django.test import Client


class CalcTests(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    def test_add_numbers(self):
        """Test adding two numbers"""
        self.assertEqual(calc.add(3, 8), 11)

    def test_subtract_numbers(self):
        """Test subtracting two numbers"""
        self.assertEqual(calc.subtract(8, 3), 5)

    def test_schema_success(self):
        """Test schema url for success"""
        url = reverse("api-schema")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_api_docs_success(self):
        """Test schema url for success"""
        url = reverse("api-docs")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
