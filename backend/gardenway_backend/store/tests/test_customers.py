from rest_framework import status
from rest_framework.test import APIClient
from store.models import User
from model_bakery import baker
import pytest


@pytest.mark.django_db
class TestCreateCustomer:

    url = '/store/customers/'

    def test_returns_201(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        client.force_authenticate(user)
        # Act
        response = client.post(self.url, {"user_id": user.id})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    def test_returns_403_from_non_admin(self):
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)
        # Act
        response = client.post(self.url, {"user_id": user.id})

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_400_from_invalid_user_id(self):
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        client.force_authenticate(user)

        # Act & Assert
        response1 = client.post(self.url, {"user_id": 500})
        assert response1.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_400_from_no_user_id(self):
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        client.force_authenticate(user)

        # Act & Assert
        response2 = client.post(self.url, {})
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_400_if_customer_exists(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        client.force_authenticate(user)

        # Act & Assert
        response3a = client.post(self.url, {"user_id": user.id})
        response3b = client.post(self.url, {"user_id": user.id})
        assert response3b.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.skip(reason="phone number validation not implemented yet")
    def test_returns_400_from_invalid_phone_number(self):
        # TODO: currently phone number validation not yet implemented

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        client.force_authenticate(user)

        # Act & Assert
        response4 = client.post(
            self.url, {"user_id": user.id, "phone": "acb"})
        assert response4.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListCustomers:
    url = '/store/customers/'

    def test_returns_200(self):

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
