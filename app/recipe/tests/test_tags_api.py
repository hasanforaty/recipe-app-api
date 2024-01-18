"""
Test for the tags API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


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
        """Test that authentication is requiere for retrieving tags"""
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
        other_user = create_user(email='other@example.com ', password='password1')
        create_tag(user=other_user, name='Blue')
        test_case = [
            create_tag(user=self.user, name='Red'),
            create_tag(user=self.user, name='Green')
        ]
        res = self.client.get(TAGS_URL)
        serializer = TagSerializer(test_case, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
