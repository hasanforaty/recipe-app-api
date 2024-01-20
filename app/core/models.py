"""
Database Models
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin)

from app import settings
import uuid
import os


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'recipe', filename)


class UserManage(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and save and return a new user"""
        if not email:
            raise ValueError('User must have and email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """Create and return a superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManage()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Recipe(models.Model):
    """Recipe Model"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    ingredients = models.ManyToManyField('Ingredient', blank=True)
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=recipe_image_file_path
    )

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tags for filtering recipes"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient Model"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
