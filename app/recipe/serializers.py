"""
Serializers for recipe API
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Class to serialise recipe model"""
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer to upload images to recipes"""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
