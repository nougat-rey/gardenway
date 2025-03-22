from rest_framework import status
from rest_framework.test import APIClient
from store.models import User
import pytest
from store.models import Product, Customer, Order
from model_bakery import baker
import uuid
from uuid import uuid4

def is_valid_uuid(input):
    try:
        uuid.UUID(str(input))
        return True
    except ValueError:
        return False


@pytest.mark.django_db
class TestCreateOrder:

    url = '/store/orders/'

    def test_returns_201(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        product = baker.make(Product)
        client.force_authenticate(user)

        # Act
        get_customer_response = client.get(f'/store/customers/me/', {"user_id":user.id})
        post_cart_response = client.post(f'/store/carts/', {"customer": get_customer_response.data['id']})
        cart_id = post_cart_response.data['id']
        data = {
            "product_id": product.id,
            "quantity": 5
        }
        post_cart_item_response = client.post(f'/store/carts/{cart_id}/items/', data)
        response = client.post(self.url, {"cart_id": str(cart_id)}, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
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

    @pytest.mark.skip(reason="Cart own permissions not implemented")
    def test_returns_400_from_cart_not_belong_to_user(self):
        # Basic Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)

        # Arrange, Act & Assert

        # 2. cart that does not belong to current user
        # TODO incomplete, skip for now
        case2_cart = self.setup_not_owned_cart()
        case2_response = client.post(self.url, {"cart_id": case2_cart.id})
        assert case2_response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_400_from_empty_cart(self):
        # Basic Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)

        # Arrange, Act & Assert
        # 3. empty cart
        case3_cart = self.setup_empty_cart(user)
        case3_response = client.post(self.url, {"cart_id": case3_cart.id})
        assert case3_response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListOrders:
    url = '/store/orders/'

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
class TestGetOrder:

    def test_returns_200_for_admin(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        order = baker.make(Order)
        client.force_authenticate(user)

        # Act
        response = client.get(f'/store/orders/{order.id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.skip(reason="Owner permission not yet implemented")
    def test_returns_200_for_owner(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        customer = baker.make(Customer, user_id=user.id)
        order = baker.make(Order, customer=customer)
        client.force_authenticate(user)

        # Act
        response = client.get(f'/store/orders/{order.id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_403_from_non_admin_and_not_owner(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        order = baker.make(Order)
        client.force_authenticate(user)

        # Act
        response = client.get(f'/store/orders/{order.id}/')

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_404(self):
        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        # Act
        response = client.get(f'/store/orders/500/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
