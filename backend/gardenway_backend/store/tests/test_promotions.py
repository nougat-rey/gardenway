import pytest
from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Promotion
from model_bakery import baker


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_user():
    return User.objects.create(is_staff=True)


@pytest.fixture
def non_admin_user():
    return User.objects.create(is_staff=False)


@pytest.fixture
def valid_data():
    return {
        "title": "test",
        "slug": "test",
        "description": "test",
        "discount": 10
    }


@pytest.fixture
def invalid_data():
    return {"title": "invalid", "slug": "test", "description": "test", "discount": 10}


@pytest.mark.django_db
class TestCreatePromotion:

    url = '/store/promotions/'

    def test_returns_201(self, client, admin_user, valid_data):
        # Arrange
        client.force_authenticate(user=admin_user)

        # Act
        response = client.post(self.url, valid_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    def test_returns_403_from_non_admin(self, client, non_admin_user, valid_data):
        # Arrange
        client.force_authenticate(user=non_admin_user)

        # Act
        response = client.post(self.url, valid_data)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("discount", [0, 100])
    def test_returns_400_from_invalid_data(self, client, admin_user, valid_data, discount):
        # Arrange
        client.force_authenticate(user=admin_user)
        data = valid_data.copy()
        data["discount"] = discount

        # Act
        response = client.post(self.url, data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListPromotions:
    url = '/store/promotions/'

    def test_returns_200(self, client):
        # Arrange
        # No setup needed for this test

        # Act
        response = client.get(self.url)

        # Assert
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGetPromotion:

    def test_returns_200(self, client):
        # Arrange
        promotion = baker.make(Promotion)

        # Act
        response = client.get(f'/store/promotions/{promotion.id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_404(self, client):
        # Act
        response = client.get(f'/store/promotions/500/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
