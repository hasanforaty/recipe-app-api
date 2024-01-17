"""
View for recipe API
"""
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer

from recipe.serializers import RecipeSerializer
from core.models import Recipe
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.settings import api_settings


class RecipeViewSet(viewsets.ModelViewSet):
    """View to manage recipe APIs"""
    serializer_class = RecipeSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
