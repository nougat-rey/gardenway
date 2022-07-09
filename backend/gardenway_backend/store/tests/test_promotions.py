from rest_framework import status
from rest_framework.test import APIClient
from store.models import User
import pytest


@pytest.mark.django_db
class TestCreatePromotion:

    url = '/store/promotions/'

    def get_valid_data(self):
        return {
            "title": "test",
            "slug": "test",
            "description": "test",
            "discount": 10
        }

    def get_invalid_data(self, key, invalid_data):
        return_dict = {"title": "invalid", "slug": "test",
                       "description": "test", "discount": 10}
        return_dict[key] = invalid_data
        return return_dict

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

        # Act & Assert

        # 1. invalid discount 0%
        response = client.post(
            self.url, self.get_invalid_data("discount", 0))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # 2. invalid discount 100%
        response = client.post(
            self.url, self.get_invalid_data("discount", 100))
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListPromotions:
    url = '/store/promotions/'

    def test_returns_200(self):

        # Arrange
        client = APIClient()

        # Act
        response = client.get(self.url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
