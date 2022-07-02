from rest_framework import status
from rest_framework.test import APIClient
from store.models import User
import pytest


@pytest.mark.django_db
class TestCreateCollection:

    url = '/store/collections/'

    def get_valid_data(self):
        return {
            "title": "test",
            "slug": "test"
        }

    def test_returns_201(self):

        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        # Act
        response = client.post(self.url, self.get_valid_data())

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    def test_returns_403_from_non_admin(self):

        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=False))

        # Act
        response = client.post(self.url, self.get_valid_data())

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_400_from_invalid_data(self):

        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        # Act
        response = client.post(self.url, {"bread": "bread"})

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
