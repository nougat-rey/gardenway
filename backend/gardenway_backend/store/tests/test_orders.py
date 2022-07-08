from rest_framework import status
from rest_framework.test import APIClient
from store.models import User
import pytest
from store.models import Cart, CartItem, Customer
from model_bakery import baker
import uuid


def is_valid_uuid(input):
    try:
        uuid.UUID(str(input))
        return True
    except ValueError:
        return False


@pytest.mark.django_db
class TestCreateOrder:

    url = '/store/orders/'

    def setup_cart(self, user):
        customer = baker.make(Customer, user_id=user.id, phone="1234567890")
        cartitem = baker.make(CartItem)
        cart = baker.make(Cart, items=[cartitem], customer=customer)
        return cart

    def setup_not_owned_cart(self):
        user = baker.make(User, is_staff=False)
        customer = baker.make(Customer, user_id=user.id, phone="0987654321")
        cartitem = baker.make(CartItem)
        cart = baker.make(Cart, items=[cartitem], customer=customer)
        return cart

    def setup_empty_cart(self, user):
        customer = baker.make(Customer, user_id=user.id, phone="1234567890")
        cart = baker.make(Cart, customer=customer)
        return cart

    def test_returns_201(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)
        cart = self.setup_cart(user)
        # Act
        response = client.post(self.url, {"cart_id": cart.id})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert is_valid_uuid(response.data['id'])

    def test_returns_403_from_anonymous(self):
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user=None)
        cart = self.setup_cart(user)

        # Act
        response = client.post(self.url, {"cart_id": cart.id})

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_400_from_invalid_data(self):
        # Basic Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)

        # Arrange, Act & Assert

        # 1. cart that does not exist
        case1_response = client.post(self.url, {"cart_id": 999})
        assert case1_response.status_code == status.HTTP_400_BAD_REQUEST

        # 2. cart that does not belong to current user
        # TODO incomplete, skip for now
        case2_cart = self.setup_not_owned_cart()
        case2_response = client.post(self.url, {"cart_id": case2_cart.id})
        assert case2_response.status_code == status.HTTP_400_BAD_REQUEST

        # 3. empty cart
        case3_cart = self.setup_empty_cart(user)
        case3_response = client.post(self.url, {"cart_id": case3_cart.id})
        assert case3_response.status_code == status.HTTP_400_BAD_REQUEST
