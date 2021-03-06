from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Product
from model_bakery import baker
import pytest


@pytest.mark.django_db
class TestCreateProduct:

    url = '/store/products/'

    def get_valid_data(self):
        return {
            "title": "test",
            "slug": "test",
            "description": "test",
            "price": 10.99,
            "inventory": 20
        }

    def get_invalid_data(self, key, invalid_data):
        return_dict = {"title": "invalid", "price": 10.99, "inventory": 20}
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

        # Act
        response = client.post(self.url, self.get_valid_data())

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_400_from_invalid_data(self):
        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        # Act & Assert

        # 1. invalid title
        response = client.post(
            self.url, self.get_invalid_data("title", 10))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # 2. invalid price
        response = client.post(
            self.url, self.get_invalid_data("price", 0))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # 3. invalid inventory
        response = client.post(
            self.url, self.get_invalid_data("inventory", -1))
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListProducts:
    url = '/store/products/'

    def test_returns_200(self):

        # Arrange
        client = APIClient()

        # Act
        response = client.get(self.url)

        # Assert
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGetProduct:

    def test_returns_200(self):

        # Arrange
        client = APIClient()
        product = baker.make(Product)

        # Act
        response = client.get(f'/store/products/{product.id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_404(self):
        # Arrange
        client = APIClient()

        # Act
        response = client.get(f'/store/products/500/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
