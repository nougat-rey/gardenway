from psutil import users
from rest_framework import status
from rest_framework.test import APIClient
from store.models import User, Product
from model_bakery import baker
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest
import uuid


def is_valid_uuid(input):
    try:
        uuid.UUID(str(input))
        return True
    except ValueError:
        return False

@pytest.mark.django_db
class TestCreateProductImage:

    def test_returns_201(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        client.force_authenticate(user)
        product = baker.make(Product)
        image_path = 'store/static/store/banner.png'
        with open(image_path, 'rb') as img:
            image_data = SimpleUploadedFile(
            name='test.png', 
            content=img.read(), 
            content_type='image/png'
            )

        # Act
        response = client.post(f'/store/products/{product.id}/images/', {'image': image_data}, format='multipart')

        # Assert
        assert response.status_code == status.HTTP_201_CREATED

    def test_returns_403_from_non_admin(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)
        product = baker.make(Product)
        image_path = 'store/static/store/banner.png'
        with open(image_path, 'rb') as img:
            image_data = SimpleUploadedFile(
            name='test.png', 
            content=img.read(), 
            content_type='image/png'
            )

        # Act
        response = client.post(f'/store/products/{product.id}/images/', {'image': image_data}, format='multipart')


        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_400_from_invalid_data(self):
        
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        client.force_authenticate(user)
        product = baker.make(Product)

        # Act
        response = client.post(f'/store/products/{product.id}/images/', {'image': "Hello World!"}, format='multipart')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestListProductImages:
    url = '/store/products/'

    def test_returns_200(self):

        # Arrange
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        product = baker.make(Product)

        # Act
        response = client.get(f'/store/products/{product.id}/images/')

        # Assert
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGetProductImages:

    def test_returns_200(self):

        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        client.force_authenticate(user)
        product = baker.make(Product)
        image_path = 'store/static/store/banner.png'
        with open(image_path, 'rb') as img:
            image_data = SimpleUploadedFile(
            name='test.png', 
            content=img.read(), 
            content_type='image/png'
            )
        post_image_response = client.post(f'/store/products/{product.id}/images/', {'image': image_data}, format='multipart')
        image_id = post_image_response.data['id']

        # Act
        response = client.get(f'/store/products/{product.id}/images/{image_id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_returns_404(self):
        # Arrange
        client = APIClient()
        user = baker.make(User, is_staff=True)
        client.force_authenticate(user)
        product = baker.make(Product)
        image_path = 'store/static/store/banner.png'
        with open(image_path, 'rb') as img:
            image_data = SimpleUploadedFile(
            name='test.png', 
            content=img.read(), 
            content_type='image/png'
            )
        post_image_response = client.post(f'/store/products/{product.id}/images/', {'image': image_data}, format='multipart')
        image_id = post_image_response.data['id']
        invalid_image_id = image_id+999
        
        # Act
        response = client.get(f'/store/products/{product.id}/images/{invalid_image_id}/')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND



