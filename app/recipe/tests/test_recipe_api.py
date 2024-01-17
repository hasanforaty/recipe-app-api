"""
Test the recipe API
"""
from django.test import TestCase
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from core.models import Recipe
from recipe.serializers import RecipeSerializer
from recipe.serializers import RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """create and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """create and return sample recipe"""
    defaults = {
        'title': 'sample recipe',
        "time_minutes": 22,
        "price": Decimal('5.25'),
        'description': 'sample description',
        'link': 'https://example.com/recipe.pdf',
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def create_user(**param):
    """Create and return new User"""
    user = get_user_model().objects.create_user(**param)
    return user


class PublicRecipeApiTests(TestCase):
    """Test the publicly available recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class PrivateRecipeApiTest(TestCase):
    """Test the authorized user recipe API"""

    def setUp(self):
        self.user = create_user(email='example@example.com', password='12345')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""
        create_recipe(user=self.user, )
        create_recipe(user=self.user, )
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""
        other_user = create_user(email='other@example.com', password='otherPassword')
        create_recipe(user=other_user, )
        create_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test retrieving recipe details"""
        recipe = create_recipe(user=self.user, )
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating Recipe successfully"""
        payload = {
            'title': 'sample recipe',
            "time_minutes": 22,
            "price": Decimal('5.25'),
            'description': 'sample description',
            'link': 'https://example.com/recipe.pdf',
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(id=res.data['id']).first()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test partial update of recipe details"""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(user=self.user, link=original_link)
        payload = {'title': 'new recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """test full update of recipe """
        recipe = create_recipe(user=self.user,
                               title='sample recipe title',
                               description='sample description',
                               link='https://example.com/recipe.pdf'
                               )
        payload = {
            'title': 'new recipe title',
            'description': 'new recipe description',
            'link': 'https://example.com/2recipe.pdf',
            'time_minutes': 10,
            'price': Decimal('2.50')
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)
