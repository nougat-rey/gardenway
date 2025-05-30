from rest_framework import status
from rest_framework.test import APIClient
from store.models import User
from model_bakery import baker
import pytest

@pytest.fixture
def authenticated_client():
    client = APIClient()
    user = baker.make(User, is_staff=True)
    client.force_authenticate(user)
    return client, user


@pytest.mark.django_db
class TestCreateCustomer:

    url = '/store/customers/'

    @pytest.mark.skip(reason="Customer automatically created due to signals/handlers")
    def test_returns_201(self, authenticated_client):
        client, user = authenticated_client

        # Act
        response = client.post(self.url, {"user_id": user.id})

        # Debugging: Print the response content to see the error message
        print(response.data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


    def test_returns_403_from_non_admin(self):
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)

        # Act
        response = client.post(self.url, {"user_id": user.id})

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_400_from_invalid_user_id(self, authenticated_client):
        client, _ = authenticated_client

        # Act
        response = client.post(self.url, {"user_id": 500})  # User does not exist
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_400_from_no_user_id(self, authenticated_client):
        client, _ = authenticated_client

        # Act
        response = client.post(self.url, {})
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_400_if_customer_exists(self, authenticated_client):
        client, user = authenticated_client

        # Act
        # Customer is already created when the user was created
        response = client.post(self.url, {"user_id": user.id})
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListCustomers:
    url = '/store/customers/'

    def test_returns_200(self, authenticated_client):
        client, _ = authenticated_client

        # Act
        response = client.get(self.url)

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_403_from_non_admin(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=False))

        # Act
        response = client.get(self.url)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestGetCustomer:

    def test_returns_200(self, authenticated_client):
        client, user = authenticated_client

        # Act
        response = client.get(f'/store/customers/me/', {"user_id": user.id})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] > 0

    def test_returns_200_from_self(self):
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)

        # Act
        response = client.get(f'/store/customers/me/', {"user_id": user.id})

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_404_client_does_not_exist(self, authenticated_client):
        client, _ = authenticated_client

        # Act
        response = client.get(f'/store/customers/500/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
