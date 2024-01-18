"""
Serializers for Recipe
"""

from rest_framework import serializers
from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag """

    class Meta:
        fields = ['name', 'id']
        read_only_fields = ['id']
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id', ]

    def create(self, validated_data):
        """Create a new recipe instance"""
        r_tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in r_tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)
        # recipe.save()
        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
