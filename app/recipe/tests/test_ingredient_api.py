from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Ingredient,Recipe
from recipe.serializers import IngredientSerializer
import random

INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Return ingredient detail id"""
    return reverse(
        'recipe:ingredient-detail',
        args=[ingredient_id]
    )


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

    def test_update_ingredient_successful(self):
        """Test updating an ingredient"""
        payload = {'name': 'Bannnana'}
        ingredient = create_ingredient(user=self.user, **payload)
        fixed = {'name': 'banana'}
        res = self.client.patch(
            detail_url(ingredient.id),
            fixed,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], fixed['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        ingredient = create_ingredient(user=self.user, name='Bannana')
        res = self.client.delete(detail_url(ingredient.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ingredient.objects.all().count(), 0)

    def test_ingredient_assigned_to_recipes(self):
        """Test Listing ingredients assigned to recipes"""
        in1 = Ingredient.objects.create(user=self.user, name='apples')
        in2 = Ingredient.objects.create(user=self.user, name='bananas')
        defaults = {
            'title': 'sample recipe',
            "time_minutes": 22,
            "price": Decimal('5.25'),
            'description': 'sample description',
            'link': 'https://example.com/recipe.pdf',
        }
        recipe = Recipe.objects.create(user=self.user,**defaults)
        recipe.ingredients.add(in1)
        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Teting filtering ingredients returned a unique list"""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        defaults = {
            'title': 'sample recipe',
            "time_minutes": 22,
            "price": Decimal('5.25'),
            'description': 'sample description',
            'link': 'https://example.com/recipe.pdf',
        }
        recipe1 = Recipe.objects.create(user=self.user, **defaults)
        defaults2 = {
            'title': 'sample recipe 2',
            "time_minutes": 222,
            "price": Decimal('25.25'),
            'description': 'sample description 2',
            'link': 'https://example.com/recipe2.pdf',
        }
        recipe2 = Recipe.objects.create(user=self.user, **defaults2)
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)
        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
