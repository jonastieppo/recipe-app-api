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

        self.user = create_user(email='user@example.com',
                                password='testpass123')

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

        other_user = create_user(email='other_example.com',
                                 password='password123')
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
            self.assertEqual(getattr(recipe, k), payload[k])

        self.assertEqual(recipe.user,  self.user)

    def test_partial_update(self):
        """Test partial update of a recipe"""
        original_link = "http://example.com/pdf"
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe Title',
            link=original_link
           )

        payload = {'title': 'New recipe Title'}
        url = detail_url(recipe_id=recipe.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self):
        """Test the full update of the recipe"""

        recipe = create_recipe(
            user=self.user,
            title='Original Title',
            link="http://example.com"
        )

        # full update
        url = detail_url(recipe_id=recipe.id)
        payload = {
            'user': create_user(
                email='user2@example.com',
                password='testpass123'
            ),
            'title': 'New Title',
            'link': 'http://example_2.com',
            'time_minutes': 10,
            'price': Decimal('2.43')
        }

        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()  # updating after db changes

        for each_k in payload.keys():
            if each_k == 'user':
                self.assertEqual(getattr(recipe, each_k), self.user)
            else:
                self.assertEqual(getattr(recipe, each_k), payload[each_k])
