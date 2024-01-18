"""
Test the recipe API
"""
from django.test import TestCase
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from core.models import (
    Recipe,
    Tag,
    Ingredient
)
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
        other_user = create_user(
            email='other@example.com',
            password='otherPassword'
        )
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

    def test_update_user_returns_error(self):
        """Test updating user by recipe result in error"""
        recipe = create_recipe(user=self.user)
        payload = {
            'user': create_user(
                email='user2@example.com',
                password='password'
            )
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting recipe successfully"""
        recipe = create_recipe(user=self.user, )
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete other users recipe give error """
        other_user = create_user(email='other2@example.com', password='pass')
        recipe = create_recipe(user=other_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_with_new_tags(self):
        """Test creating a new recipe with new Tags"""
        payload = {
            'title': 'new recipe title',
            'description': 'new recipe description',
            'link': 'https://example.com/2recipe.pdf',
            'time_minutes': 10,
            'price': Decimal('2.50'),
            'tags': [
                {'name': 'python'},
                {'name': 'cheese'},
            ]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes.first()

        self.assertEqual(recipe.tags.count(), 2)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tags"""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payloads = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 10,
            'price': Decimal('2.50'),
            'description': "new recipe description",
            'tags': [
                {'name': tag_indian.name},
                {'name': "Breakfast"}
            ]
        }
        res = self.client.post(RECIPE_URL, payloads, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())

    def test_create_tag_on_Update(self):
        """Test creating a tag , updating recipe"""
        recipe = create_recipe(self.user)
        payload = {'tags': [{'name': 'Breakfast'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.tags.count(), 1)

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        pyload = {'tags': [{'name': tag_lunch.name}]}
        res = self.client.patch(detail_url(recipe.id), pyload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clearing_recipe_tags(self):
        """Test clearing a recipe tags"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)
        payload = {'tags': []}
        res = self.client.patch(detail_url(recipe.id), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.tags.count(), 0)

    def test_creating_recipe_with_ingredients(self):
        """Test creating a new Recipe with new Ingredients"""
        payloads = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 10,
            'price': Decimal('2.50'),
            'description': "new recipe description",
            'ingredients': [
                {'name': 'bread'},
                {'name': 'chicken'}
            ]
        }
        res = self.client.post(RECIPE_URL, payloads, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res.data['ingredients']), 2)

    def test_creating_recipe_with_existing_ingredient(self):
        """Test creating a new recipe with existing ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name='Meat')
        payloads = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 10,
            'price': Decimal('2.50'),
            'description': "new recipe description",
            'ingredients': [
                {'name': ingredient.name},
                {'name': 'chicken'}
            ]
        }
        res = self.client.post(RECIPE_URL, payloads, format='json')
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes.first()
        self.assertIn(ingredient, recipe.ingredients.all())
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_updating_recipe_with_new_ingredients(self):
        """Test updating recipe with new ingredients"""
        payloads = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 10,
            'price': Decimal('2.50'),
            'description': "new recipe description",
        }
        recipe = create_recipe(user=self.user, **payloads)
        ingredient = Ingredient.objects.create(user=self.user, name='Chicken')
        recipe.ingredients.add(ingredient)

        new_ingredient = Ingredient.objects.create(user=self.user, name='Meat')
        res = self.client.patch(
            detail_url(recipe.id),
            {'ingredients': [{'name': new_ingredient.name}]},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertEqual(recipe.ingredients.all()[0].name, new_ingredient.name)
        self.assertEqual(recipe.ingredients.all()[0].id, new_ingredient.id)

    def test_clearing_recipe_ingredient(self):
        """Test clearing recipe ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='garlic')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)
        payload = {'ingredients': []}
        res = self.client.patch(detail_url(recipe.id), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.ingredients.count(), 0)
