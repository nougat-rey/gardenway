import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.conf import settings
import tempfile
import shutil

@pytest.fixture
def create_user(db):
    def make_user(username="testuser", password="testpassword"):
        User = get_user_model()
        return User.objects.create_user(username=username, password=password)
    return make_user

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture(autouse=True)
def temp_media_root(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    yield
    # No need to clean manually; tmp_path gets auto-deleted
