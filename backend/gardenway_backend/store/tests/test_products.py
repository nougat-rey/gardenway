from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import pytest


@pytest.mark.django_db
class TestCreateProduct:
    def test_returns_201(self):

        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        # Act

        response = client.post('/store/products/',
                               {
                                   "title": "test",
                                   "slug": "test",
                                   "description": "test",
                                   "price": 10.99,
                                   "inventory": 20
                               }
                               )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
