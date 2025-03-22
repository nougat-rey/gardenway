from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Product
from model_bakery import baker
import pytest

"""
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
"""


@pytest.mark.django_db
class TestCreateProductReview:

    def test_returns_201(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)
        product = baker.make(Product)
        data = {
            "product": product.id,
            "rating": 5,
            "name": "Great Product",
            "description": "I really loved this product. It exceeded my expectations!",
            "date": "2022-05-30"
        }

        # Act
        response = client.post(f'/store/products/{product.id}/reviews/', data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED

    def test_returns_403_from_anonymous(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        product = baker.make(Product)
        data = {
            "product": product.id,
            "rating": 5,
            "name": "Great Product",
            "description": "I really loved this product. It exceeded my expectations!",
            "date": "2022-05-30"
        }

        # Act
        response = client.post(f'/store/products/{product.id}/reviews/', data)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_400_from_invalid_data(self):
        
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)
        product = baker.make(Product)
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

    def test_returns_200(self):

        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=False))
        product = baker.make(Product)

        # Act
        response = client.get(f'/store/products/{product.id}/reviews/')

        # Assert
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGetProductReview:

    def test_returns_200(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)
        product = baker.make(Product)
        data = {
            "product": product.id,
            "rating": 5,
            "name": "Great Product",
            "description": "I really loved this product. It exceeded my expectations!",
            "date": "2022-05-30"
        }
        client.post(f'/store/products/{product.id}/reviews/', data)

        # Act
        response = client.get(f'/store/products/{product.id}/reviews/{1}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_404(self):
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)
        product = baker.make(Product)
        data = {
            "product": product.id,
            "rating": 5,
            "name": "Great Product",
            "description": "I really loved this product. It exceeded my expectations!",
            "date": "2022-05-30"
        }
        client.post(f'/store/products/{product.id}/reviews/', data)

        # Act
        response = client.get(f'/store/products/{product.id}/reviews/{999}/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


