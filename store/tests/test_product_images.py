from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Product
from model_bakery import baker
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest


# Global fixture for authenticated client
@pytest.fixture
def authenticated_client():
    client = APIClient()
    user = baker.make(User, is_staff=True)  # Admin user
    client.force_authenticate(user)
    return client


# Global fixture for creating a product
@pytest.fixture
def product():
    return baker.make(Product)


# Global fixture for preparing image data for testing
@pytest.fixture
def image_data():
    image_path = 'store/static/store/banner.png'
    with open(image_path, 'rb') as img:
        return SimpleUploadedFile(name='test.png', content=img.read(), content_type='image/png')


@pytest.mark.django_db
class TestCreateProductImage:

    def test_create_product_image_returns_201(self, authenticated_client, product, image_data):
        # Act
        response = authenticated_client.post(
            f'/store/products/{product.id}/images/', {'image': image_data}, format='multipart'
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_product_image_returns_403_from_non_admin(self, product, image_data):
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)

        # Act
        response = client.post(
            f'/store/products/{product.id}/images/', {'image': image_data}, format='multipart'
        )
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_product_image_returns_400_from_invalid_data(self, authenticated_client, product):
        # Act
        response = authenticated_client.post(
            f'/store/products/{product.id}/images/', {'image': "Hello World!"}, format='multipart'
        )
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListProductImages:

    def test_list_product_images_returns_200(self, authenticated_client, product):
        # Act
        response = authenticated_client.get(f'/store/products/{product.id}/images/')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGetProductImage:

    def test_get_product_image_returns_200(self, authenticated_client, product, image_data):
        # Act
        post_image_response = authenticated_client.post(
            f'/store/products/{product.id}/images/', {'image': image_data}, format='multipart'
        )
        image_id = post_image_response.data['id']
        
        response = authenticated_client.get(f'/store/products/{product.id}/images/{image_id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_get_product_image_returns_404(self, authenticated_client, product, image_data):
        post_image_response = authenticated_client.post(
            f'/store/products/{product.id}/images/', {'image': image_data}, format='multipart'
        )
        image_id = post_image_response.data['id']
        invalid_image_id = image_id + 999  # Simulating an invalid image ID

        # Act
        response = authenticated_client.get(f'/store/products/{product.id}/images/{invalid_image_id}/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
