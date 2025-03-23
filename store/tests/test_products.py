import pytest
from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Product
from model_bakery import baker


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_user():
    return baker.make(User, is_staff=True)


@pytest.fixture
def non_admin_user():
    return baker.make(User, is_staff=False)


@pytest.fixture
def valid_product_data():
    return {
        "title": "test",
        "slug": "test",
        "description": "test",
        "price": 10.99,
        "inventory": 20
    }


@pytest.fixture
def invalid_product_data():
    return {
        "title": "invalid", "price": 10.99, "inventory": 20
    }


@pytest.mark.django_db
class TestCreateProduct:
    url = '/store/products/'

    def test_returns_201(self, client, admin_user, valid_product_data):
        # Arrange
        client.force_authenticate(user=admin_user)

        # Act
        response = client.post(self.url, valid_product_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    def test_returns_403_from_non_admin(self, client, non_admin_user, valid_product_data):
        # Arrange
        client.force_authenticate(user=non_admin_user)

        # Act
        response = client.post(self.url, valid_product_data)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("key, invalid_data", [
        ("price", 0),
        ("inventory", -1)
    ])
    def test_returns_400_from_invalid_data(self, client, admin_user, valid_product_data, key, invalid_data):
        
        # Arrange
        client.force_authenticate(user=admin_user)
        data = valid_product_data.copy()
        data[key] = invalid_data

        # Act
        response = client.post(self.url, data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListProducts:

    def test_returns_200(self, client):
        # Arrange
        # No setup needed for this test

        # Act
        response = client.get('/store/products/')

        # Assert
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGetProduct:

    def test_returns_200(self, client):
        # Arrange
        product = baker.make(Product)

        # Act
        response = client.get(f'/store/products/{product.id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_404(self, client):
        # Act
        response = client.get('/store/products/500/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
