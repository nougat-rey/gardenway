from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Cart
from model_bakery import baker
import pytest
import uuid


def is_valid_uuid(input):
    try:
        uuid.UUID(str(input))
        return True
    except ValueError:
        return False


@pytest.fixture
def authenticated_client():
    client = APIClient()
    user = baker.make(User, is_staff=False)
    client.force_authenticate(user)
    return client, user


@pytest.fixture
def authenticated_admin_client():
    client = APIClient()
    user = baker.make(User, is_staff=True)
    client.force_authenticate(user)
    return client, user


@pytest.fixture
def customer(authenticated_client):
    client, user = authenticated_client
    response = client.get(f'/store/customers/me/', {"user_id": user.id})
    return response.data['id']


@pytest.fixture
def cart(authenticated_client, customer):
    client, user = authenticated_client
    response = client.post('/store/carts/', {"customer": customer})
    return response.data


@pytest.mark.django_db
class TestCreateCart:

    url = '/store/carts/'

    def test_returns_201(self, authenticated_client, customer):
        client, _ = authenticated_client

        response = client.post(self.url, {"customer": customer})

        assert response.status_code == status.HTTP_201_CREATED
        assert is_valid_uuid(response.data['id'])

    def test_returns_401_from_anonymous(self, customer):
        client = APIClient()
        client.logout()
        response = client.post(self.url, {"customer": customer})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_400_from_invalid_data(self, authenticated_admin_client):
        client, _ = authenticated_admin_client

        # 1. customer does not exist
        response = client.post(self.url, {"customer": 999})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListCarts:
    url = '/store/carts/'

    def test_returns_200(self, authenticated_admin_client):
        client, _ = authenticated_admin_client
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_returns_403_from_non_admin(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestGetCart:

    def test_returns_200_for_admin(self, authenticated_admin_client, cart):
        client, _ = authenticated_admin_client
        response = client.get(f'/store/carts/{cart["id"]}/')
        assert response.status_code == status.HTTP_200_OK

    def test_returns_200_for_owner(self, authenticated_client, cart):
        client, _ = authenticated_client
        response = client.get(f'/store/carts/{cart["id"]}/')
        assert response.status_code == status.HTTP_200_OK

    def test_returns_403_from_non_admin_and_not_owner(self, authenticated_client, cart):
        client, _ = authenticated_client
        client.logout()
        
        other_user = baker.make(User, is_staff=False)
        client.force_authenticate(other_user)

        response = client.get(f'/store/carts/{cart["id"]}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_404(self, authenticated_admin_client):
        client, _ = authenticated_admin_client
        response = client.get(f'/store/carts/500/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
