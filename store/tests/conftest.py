import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

@pytest.fixture
def create_user(db):
    def make_user(username="testuser", password="testpassword"):
        User = get_user_model()
        return User.objects.create_user(username=username, password=password)
    return make_user

@pytest.fixture
def api_client():
    return APIClient()
