"""
View for recipe API
"""
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from core.models import Recipe
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.settings import api_settings


class RecipeViewSet(viewsets.ModelViewSet):
    """View to manage recipe APIs"""
    serializer_class = RecipeDetailSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer base on action of user"""
        if self.action == 'list':
            return RecipeSerializer
        else:
            return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe """
        serializer.save(user=self.request.user)

