"""
Database Models
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin)

from app import settings


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    link = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title
