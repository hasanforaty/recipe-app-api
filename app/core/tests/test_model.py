"""
test for model
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


class ModelTests(TestCase):
    """Test model"""

    def test_create_user_with_email_successful(self):
        """Test creating User with an email is successful"""
        email = 'test@example.com'
        password = 'test'
        user = get_user_model().objects.create_user(
            email=email, password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""

        test_cases = [
            ['teSt@examPle.com', 'teSt@example.com'],
            ['TEST@EXAMPLE.COM', 'TEST@example.com'],
            ['Test@Example.Com', 'Test@example.com']
        ]
        for email, expected_email in test_cases:
            user = get_user_model().objects.create_user(
                email=email, password='password'
            )
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'password')

    def test_create_new_superuser(self):
        """Test creating and saving new superuser"""
        email = 'test@example.com'
        user = (get_user_model().objects.
                create_superuser(email=email, password='password'))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, email)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com', 'password'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description'
        )
        self.assertEqual(str(recipe), recipe.title)
