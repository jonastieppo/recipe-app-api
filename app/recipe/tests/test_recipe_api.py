"""
Test for recipe APIs
"""
from decimal import Decimal

from django.contrib.auth import get_user_model

from django.test import TestCase

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    )

RECIPES_URL = reverse('recipe:recipe-list')

def create_user(**params):
    """Creates and return a new user"""
    return get_user_model().objects.create_user(**params)

def detail_url(recipe_id):
    """Creates and return a recipe detail urls"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'sample recipe title',
        'time_minutes': 22,
        'price': Decimal(2),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf'

    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Tests auth is required API"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test for recipe list retrieve"""
        create_recipe(user=self.user),
        create_recipe(user=self.user),

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        '''Test list of recipe is limited to user'''
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123'
        )

        create_recipe(other_user)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creates recipe."""
        payload = {
            'title': 'Example recipe',
            'time_minutes': 5,
            'price': Decimal('20.0'),
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # getting from db

        recipe = Recipe.objects.get(id=res.data['id'])
        for k in payload.keys():
            self.assertEqual(getattr(recipe,k), payload[k])

        self.assertEqual(recipe.user, self.user)
