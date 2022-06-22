from rest_framework import status
from rest_framework.test import APIClient
import pytest


@pytest.mark.django_db
class TestCreateProduct:
    def test_returns_201(self):

        # Arrange
        # none required

        # Act
        client = APIClient()
        response = client.post('/store/collections/',
                               {
                                   'title': 'test',
                                   'slug': 'test',
                                   'description': 'test',
                                   'unit_price': 10.99,
                                   'inventory': 20
                               }
                               )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
