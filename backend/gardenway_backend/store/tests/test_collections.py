from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import pytest


@pytest.mark.django_db
class TestCreateCollection:
    def test_returns_201(self):

        # Arrange
        # none required

        # Act
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        response = client.post('/store/collections/', {'title': 'a'})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
