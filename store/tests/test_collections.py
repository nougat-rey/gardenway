from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Collection
from model_bakery import baker
import pytest


@pytest.fixture
def admin_user():
    return baker.make(User, is_staff=True)


@pytest.fixture
def non_admin_user():
    return baker.make(User, is_staff=False)


@pytest.fixture
def authenticated_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def non_authenticated_client():
    return APIClient()


@pytest.mark.django_db
class TestCreateCollection:
    url = '/store/collections/'

    def get_valid_data(self):
        return {
            "title": "test",
            "slug": "test"
        }

    def test_returns_201(self, authenticated_client):
        # Act
        response = authenticated_client.post(self.url, self.get_valid_data())

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    def test_returns_403_from_non_admin(self, non_admin_user):
        # Arrange
        client = APIClient()
        client.force_authenticate(user=non_admin_user)

        # Act
        response = client.post(self.url, self.get_valid_data())

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_400_from_invalid_data(self, authenticated_client):
        # Act
        response = authenticated_client.post(self.url, {"bread": "bread"})

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListCollections:
    url = '/store/collections/'

    def test_returns_200(self, non_authenticated_client):
        # Act
        response = non_authenticated_client.get(self.url)

        # Assert
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGetCollection:

    def test_returns_200(self, non_authenticated_client):
        # Arrange
        collection = baker.make(Collection)

        # Act
        response = non_authenticated_client.get(f'/store/collections/{collection.id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_404(self, non_authenticated_client):
        # Act
        response = non_authenticated_client.get(f'/store/collections/500/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
