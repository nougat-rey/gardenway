import pytest
from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Product
from model_bakery import baker


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return baker.make(User, is_staff=False)


@pytest.fixture
def admin_user():
    return baker.make(User, is_staff=True)


@pytest.fixture
def product():
    return baker.make(Product)


@pytest.fixture
def review_data(product):
    return {
        "product": product.id,
        "rating": 5,
        "name": "Great Product",
        "description": "I really loved this product. It exceeded my expectations!",
        "date": "2022-05-30"
    }


@pytest.mark.django_db
class TestCreateProductReview:

    def test_returns_201(self, client, user, product, review_data):
        # Arrange
        client.force_authenticate(user=user)

        # Act
        response = client.post(f'/store/products/{product.id}/reviews/', review_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED

    def test_returns_401_from_anonymous(self, client, product, review_data):
        # Act
        response = client.post(f'/store/products/{product.id}/reviews/', review_data)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_400_from_invalid_data(self, client, user, product):
        # Arrange
        client.force_authenticate(user=user)
        data = {
            "rating": 5,
            "name": "Great Product",
            "description": "I really loved this product. It exceeded my expectations!",
            "date": "2022-05-30"
        }

        # Act
        response = client.post(f'/store/products/{product.id}/reviews/', data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListProductReviews:

    def test_returns_200(self, client, user, product):
        # Arrange
        client.force_authenticate(user=user)

        # Act
        response = client.get(f'/store/products/{product.id}/reviews/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
