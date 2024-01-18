from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Ingredient
from recipe.serializers import IngredientSerializer
import random

INGREDIENT_URL = reverse('recipe:ingredient-list')


def create_ingredient(user, **argument):
    payload = {'name': f'Test Ingredient_{random.randint(0, 100)}'}
    payload.update(argument)
    ingredient = Ingredient.objects.create(user=user, **payload)
    return ingredient


class PublicIngredientApiTests(TestCase):
    """Test Ingredient unauthorized Api calls"""

    def setUp(self):
        self.client = APIClient()

    def test_denied_unauthorized_access(self):
        """Test return 401 Unauthorized access for unauthorized access"""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test Ingredient Api for Authorized user"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients"""
        create_ingredient(user=self.user)
        create_ingredient(user=self.user)
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(serializer.data, res.data)

    def test_ingredients_limited_to_user(self):
        """Test retrieving ingredients for only creator of ingredient"""
        other_user = get_user_model().objects.create_user(
            email='test1@example.com',
            password='test2'
        )
        other_user_ingredient = create_ingredient(user=other_user)
        create_ingredient(user=self.user)
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        for ingredient in res.data:
            self.assertNotEquals(
                other_user_ingredient.name,
                ingredient['name']
            )
