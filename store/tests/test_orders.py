from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Product, Order, Customer
import pytest
from model_bakery import baker
import uuid


def is_valid_uuid(input):
    try:
        uuid.UUID(str(input))
        return True
    except ValueError:
        return False


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

    def test_returns_200_and_all_orders_for_admin(self):
        admin_user = baker.make(User, is_staff=True)

        user1 = baker.make(User)
        user2 = baker.make(User)

        customer1 = Customer.objects.get(user=user1)
        customer2 = Customer.objects.get(user=user2)

        baker.make('store.Order', customer=customer1, _quantity=2)
        baker.make('store.Order', customer=customer2, _quantity=3)

        client = APIClient()
        client.force_authenticate(user=admin_user)

        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_returns_200_and_only_own_orders_for_non_admin(self):
        user = baker.make(User, is_staff=False)
        customer = Customer.objects.get(user=user)

        baker.make('store.Order', customer=customer, _quantity=2)

        other_user = baker.make(User)
        other_customer = Customer.objects.get(user=other_user)
        baker.make('store.Order', customer=other_customer, _quantity=3)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        for order in response.data:
            assert order['customer'] == customer.id

    def test_does_not_return_other_users_orders_for_non_admin(self):
        user = baker.make(User, is_staff=False)
        customer = Customer.objects.get(user=user)

        other_user = baker.make(User)
        other_customer = Customer.objects.get(user=other_user)
        baker.make('store.Order', customer=other_customer, _quantity=3)

        user_orders = baker.make('store.Order', customer=customer, _quantity=1)

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        returned_ids = {order['id'] for order in response.data}
        expected_ids = {str(order.id) for order in user_orders}

        assert returned_ids == expected_ids


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
