from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Product, Cart
from model_bakery import baker
import pytest


@pytest.mark.django_db
class TestCreateCartItem:

    def test_returns_201(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        product = baker.make(Product)
        client.force_authenticate(user)
        get_customer_response = client.get(f'/store/customers/me/', {"user_id":user.id})
        post_cart_response = client.post('/store/carts/', {"customer": get_customer_response.data['id']})
        cart_id = post_cart_response.data['id']
        data = {
            "product_id": product.id,
            "quantity": 5
        }

        # Act
        response = client.post(f'/store/carts/{cart_id}/items/', data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED

    def test_returns_403_from_anonymous(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        product = baker.make(Product)
        client.force_authenticate(user)
        get_customer_response = client.get(f'/store/customers/me/', {"user_id":user.id})
        post_cart_response = client.post('/store/carts/', {"customer": get_customer_response.data['id']})
        cart_id = post_cart_response.data['id']
        data = {
            "product_id": product.id,
            "quantity": 5
        }
        client.logout()

        # Act
        response = client.post(f'/store/carts/{cart_id}/items/', data)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_400_from_invalid_data(self):
        
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        product = baker.make(Product)
        client.force_authenticate(user)
        get_customer_response = client.get(f'/store/customers/me/', {"user_id":user.id})
        post_cart_response = client.post('/store/carts/', {"customer": get_customer_response.data['id']})
        cart_id = post_cart_response.data['id']
        data = {
            "product_id": product.id,
            "quantity": -1
        }

        # Act
        response = client.post(f'/store/carts/{cart_id}/items/', data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListCartItems:

    def test_returns_200(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        product = baker.make(Product)
        client.force_authenticate(user)
        get_customer_response = client.get(f'/store/customers/me/', {"user_id":user.id})
        post_cart_response = client.post('/store/carts/', {"customer": get_customer_response.data['id']})
        cart_id = post_cart_response.data['id']
        data = {
            "product_id": product.id,
            "quantity": 5
        }
        client.post(f'/store/carts/{cart_id}/items/', data)

        # Act
        response = client.get(f'/store/carts/{cart_id}/items/')

        # Assert
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGetCartItem:

    def test_returns_200(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        product = baker.make(Product)
        client.force_authenticate(user)
        get_customer_response = client.get(f'/store/customers/me/', {"user_id":user.id})
        post_cart_response = client.post('/store/carts/', {"customer": get_customer_response.data['id']})
        cart_id = post_cart_response.data['id']
        data = {
            "product_id": product.id,
            "quantity": 5
        }
        post_cart_item_response = client.post(f'/store/carts/{cart_id}/items/', data)
        cart_item_id = post_cart_item_response.data['id']

        # Act
        response = client.get(f'/store/carts/{cart_id}/items/{cart_item_id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_404(self):
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        product = baker.make(Product)
        client.force_authenticate(user)
        get_customer_response = client.get(f'/store/customers/me/', {"user_id":user.id})
        post_cart_response = client.post('/store/carts/', {"customer": get_customer_response.data['id']})
        cart_id = post_cart_response.data['id']
        data = {
            "product_id": product.id,
            "quantity": 5
        }
        post_cart_item_response = client.post(f'/store/carts/{cart_id}/items/', data)
        cart_item_id = post_cart_item_response.data['id']

        # Act
        response = client.get(f'/store/carts/{cart_id}/items/{999}/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


