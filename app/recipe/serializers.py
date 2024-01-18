"""
Serializers for Recipe
"""

from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag """

    class Meta:
        model = Tag
        fields = ['id', 'name', ]
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe"""
    tags = TagSerializer(many=True, required=False, read_only=False)
    ingredients = IngredientSerializer(many=True, required=False, read_only=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id', ]

    def _get_or_create_tags(self, tags, recipe, auth_user):
        """Handle getting or creating tags """

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe, auth_user):
        """Handle getting or creating ingredients """
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(user=auth_user, **ingredient)
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a new recipe instance"""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        auth_user = self.context['request'].user
        # add user to Recipe
        recipe = Recipe.objects.create(**validated_data, user=auth_user)
        self._get_or_create_tags(tags, recipe, auth_user=auth_user)
        self._get_or_create_ingredients(ingredients, recipe, auth_user=auth_user)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe with Tags"""
        auth_user = self.context['request'].user
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance, auth_user)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance, auth_user)
        for att, value in validated_data.items():
            setattr(instance, att, value)
        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
