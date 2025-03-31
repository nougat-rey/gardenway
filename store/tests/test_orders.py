from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Product, Cart, Order
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
@pytest.fixture
def setup_data():
    user = baker.make(User, is_staff=False)
    product = baker.make(Product)
    client = APIClient()
    client.force_authenticate(user)
    get_customer_response = client.get(f'/store/customers/me/', {"user_id": user.id})
    post_cart_response = client.post(f'/store/carts/', {"customer": get_customer_response.data['id']})
    cart_id = post_cart_response.data['id']
    return {
        "client": client,
        "user": user,
        "product": product,
        "cart_id": cart_id
    }


@pytest.mark.django_db
class TestCreateOrder:
    url = '/store/orders/'

    def test_returns_201(self, setup_data):
        client = setup_data["client"]
        product = setup_data["product"]
        cart_id = setup_data["cart_id"]

        data = {
            "product_id": product.id,
            "quantity": 5
        }
        post_cart_item_response = client.post(f'/store/carts/{cart_id}/items/', data)
        response = client.post(self.url, {"cart_id": str(cart_id)}, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert is_valid_uuid(response.data['id'])
        assert post_cart_item_response.data['product_id'] == response.data['items'][0]['product']['id']
        assert post_cart_item_response.data['quantity'] == response.data['items'][0]['quantity']

    def test_returns_401_from_anonymous(self, setup_data):
        client = setup_data["client"]
        cart_id = setup_data["cart_id"]

        client.logout()
        response = client.post(self.url, {"cart_id": str(cart_id)}, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_401_from_cart_not_belong_to_user(self, setup_data):
        client = setup_data["client"]
        cart_id = setup_data["cart_id"]

        client.logout()
        other_user = baker.make(User, is_staff=False)
        client.force_login(other_user)
        response = client.post(self.url, {"cart_id": str(cart_id)}, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_403_from_invalid_data(self, setup_data):
        client = setup_data["client"]

        response = client.post(self.url, {"cart_id": "Hello World!"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_403_from_empty_cart(self, setup_data):
        client = setup_data["client"]
        cart_id = setup_data["cart_id"]

        response = client.post(self.url, {"cart_id": str(cart_id)}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestListOrders:
    url = '/store/orders/'

    def test_returns_200(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_returns_403_from_non_admin(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=False))

        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestGetOrder:

    def test_returns_200_for_admin(self, setup_data):
        client = setup_data["client"]
        cart_id = setup_data["cart_id"]

        data = {
            "product_id": setup_data["product"].id,
            "quantity": 5
        }
        post_cart_item_response = client.post(f'/store/carts/{cart_id}/items/', data)
        post_order_response = client.post(f'/store/orders/', {"cart_id": str(cart_id)}, format='json')
        order_id = post_order_response.data['id']

        response = client.get(f'/store/orders/{order_id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_returns_200_for_owner(self, setup_data):
        client = setup_data["client"]
        cart_id = setup_data["cart_id"]

        data = {
            "product_id": setup_data["product"].id,
            "quantity": 5
        }
        post_cart_item_response = client.post(f'/store/carts/{cart_id}/items/', data)
        post_order_response = client.post(f'/store/orders/', {"cart_id": str(cart_id)}, format='json')
        order_id = post_order_response.data['id']

        response = client.get(f'/store/orders/{order_id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_returns_403_from_non_admin_and_not_owner(self, setup_data):
        client = setup_data["client"]
        cart_id = setup_data["cart_id"]

        data = {
            "product_id": setup_data["product"].id,
            "quantity": 5
        }
        post_cart_item_response = client.post(f'/store/carts/{cart_id}/items/', data)
        post_order_response = client.post(f'/store/orders/', {"cart_id": str(cart_id)}, format='json')
        order_id = post_order_response.data['id']
        client.logout()
        other_user = baker.make(User, is_staff=False)
        client.force_authenticate(other_user)

        response = client.get(f'/store/orders/{order_id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_404(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        response = client.get(f'/store/orders/500/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
