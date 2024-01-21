"""
Test for the tags API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from decimal import Decimal


from core.models import Tag,Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def tag_detail_url(tag_id):
    """Return tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testPass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email=email, password=password)


def create_tag(user, **params):
    """Create a sample tag"""
    defaults = {'name': 'avacado'}
    defaults.update(params)
    return Tag.objects.create(user=user, **defaults)


class PublicTagsApiTests(TestCase):
    """Test Unauthenticated user tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test authenticated user tags API"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving List of tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test retrieving tags for only the authenticated user"""
        other_user = create_user(
            email='other@example.com ',
            password='password1'
        )
        create_tag(user=other_user, name='Blue')
        test_case = [
            create_tag(user=self.user, name='Red'),
            create_tag(user=self.user, name='Green')
        ]
        res = self.client.get(TAGS_URL)
        serializer = TagSerializer(test_case, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # def test_create_tag_successful(self):
    #     """Test creating tags successful"""
    #     payload = {'name': 'Fruity'}
    #     res = self.client.post(TAGS_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     exists = Tag.objects.filter(name=payload['name']).exists()
    #     self.assertTrue(exists)
    #
    # def test_updating_user_of_tags_unsuccessful(self):
    #     """Test updating user of tags unsuccessful"""
    #     tag = create_tag(self.user, name='Green')
    #     other_user = create_user('other@example.com', 'password')
    #     payload = {'user': other_user}
    #     res = self.client.patch(tag_detail_url(tag.id), payload)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertTrue(
    #     Tag.objects.filter(
    #       user=self.user,
    #       name=tag.name
    #       ).exists()
    #     )
    #     self.assertFalse(
    #     Tag.objects.filter(
    #       user=other_user,
    #       name=tag.name
    #       ).exists()
    #     )

    def test_delete_tag(self):
        """Test deleting a Tag"""
        tag = create_tag(self.user, name='Red')
        res = self.client.delete(tag_detail_url(tag.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Tag.objects.filter(
                user=self.user,
                name=tag.name
            ).exists()
        )

    def test_updating_tags_successful(self):
        """Test updating tags successful"""
        payload = {'name': 'Goad Food'}
        tag = create_tag(self.user, **payload)
        new_name = 'Good Food'
        res = self.client.patch(tag_detail_url(tag.id), {'name': new_name})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertTrue(tag.name == new_name)

    def test_filter_tag_assigned_to_recipes(self):
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        defaults = {
            'title': 'sample recipe',
            "time_minutes": 22,
            "price": Decimal('5.25'),
            'description': 'sample description',
            'link': 'https://example.com/recipe.pdf',
        }
        recipe1 = Recipe.objects.create(user=self.user, **defaults)
        recipe1.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags return a unique list"""
        tag = Tag.objects.create(user=self.user, name='Breakfeast')
        Tag.objects.create(user=self.user, name='Lunch')
        default1 = {
            'title': 'sample recipe',
            "time_minutes": 22,
            "price": Decimal('5.25'),
            'description': 'sample description',
            'link': 'https://example.com/recipe.pdf',
        }
        recipe1 = Recipe.objects.create(user=self.user, **default1)
        default2 = {
            'title': 'sample recipe2',
            "time_minutes": 22,
            "price": Decimal('5.25'),
            'description': 'sample description2',
            'link': 'https://example.com/recipe.pdf',
        }
        recipe2 = Recipe.objects.create(user=self.user, **default2)
        recipe2.tags.add(tag)
        recipe1.tags.add(tag)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)


