from psutil import users
from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Customer, Cart
import pytest
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


@pytest.mark.django_db
class TestGetCart:

    def test_returns_200_for_admin(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        cart = baker.make(Cart)
        client.force_authenticate(user)

        # Act
        response = client.get(f'/store/carts/{cart.id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    # @pytest.mark.skip(reason="Owner permission not yet implemented")
    def test_returns_200_for_owner(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        customer = baker.make(Customer, user_id=user.id)
        cart = baker.make(Cart, customer=customer)
        client.force_authenticate(user)

        # Act
        response = client.get(f'/store/carts/{cart.id}/')
        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_403_from_non_admin_and_not_owner(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        cart = baker.make(Cart)
        client.force_authenticate(user)

        # Act
        response = client.get(f'/store/carts/{cart.id}/')

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_404(self):
        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        # Act
        response = client.get(f'/store/carts/500/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
