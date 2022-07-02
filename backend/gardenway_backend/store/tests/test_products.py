from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import pytest


@pytest.mark.django_db
class TestCreateProduct:
    def test_returns_201(self):

        # Arrange
        # none required

        # Act
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        response = client.post('/store/products/',
                               {
                                   "title": "test",
                                   "slug": "test",
                                   "description": "test",
                                   "price": 10.99,
                                   "inventory": 20
                               }
                               )
        print("Test")
        print(response.data)
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
