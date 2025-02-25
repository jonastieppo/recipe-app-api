"""
Test for models
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Creta and return a new user"""
    return get_user_model().objects.create_user(
        email=email,
        password=password
        )


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_sucessful(self):
        """Test creating a user with an email is sucessful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@ExAMPLE.com', 'Test2@example.com'],
            ['TEST3@ExAMPLE.com', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test recipe creation"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        title = 'Sample recipe NAME'

        recipe = models.Recipe.objects.create(
            user=user,
            title=title,
            time_minutes=5,
            price=Decimal(5.5),
            description='Sample recipe'
        )

        self.assertEqual(str(recipe), title)

    def test_tag_create(self):
        """Tests tag creation"""
        user = create_user()
        tag = models.Tag.objects.create(
            user=user,
            name='Tag1'
        )

        self.assertEqual(str(tag), tag.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
