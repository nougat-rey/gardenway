from rest_framework import status
from rest_framework.test import APIClient
from store.models import User
import pytest
from store.models import Customer
from model_bakery import baker
import uuid


def is_valid_uuid(input):
    try:
        uuid.UUID(str(input))
        return True
    except ValueError:
        return False


@pytest.mark.django_db
class TestCreateCart:

    url = '/store/carts/'

    def test_returns_201(self):

        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        customer = baker.make(Customer)

        # Act
        response = client.post(self.url, {"customer": customer.id})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert is_valid_uuid(response.data['id'])

    def test_returns_403_from_anonymous(self):

        # Arrange
        client = APIClient()
        customer = baker.make(Customer)

        # Act
        response = client.post(self.url, {"customer": customer.id})

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_400_from_invalid_data(self):
        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        # Act & Assert

        # 1. customer does not exist
        response = client.post(self.url, {"customer": 999})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListCarts:
    url = '/store/carts/'

    def test_returns_201(self):

        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        # Act
        response = client.get(self.url)

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_403_from_non_admin(self):

        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=False))

        # Act
        response = client.get(self.url)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
