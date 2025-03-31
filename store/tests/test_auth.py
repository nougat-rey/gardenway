import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_jwt_authentication(api_client, create_user):
    """Test obtaining and using JWT tokens."""

    # Create test user
    user = create_user()

    # Step 1: Get JWT token
    url = reverse("jwt-create")  # Endpoint: /auth/jwt/create/
    response = api_client.post(url, {"username": user.username, "password": "testpassword"}, format="json")

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data

    access_token = response.data["access"]
    refresh_token = response.data["refresh"]

    # Step 2: Use JWT token to access a protected endpoint
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    url = reverse("user-me")  # Endpoint: /auth/users/me/
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["username"] == user.username

    return access_token, refresh_token


@pytest.mark.django_db
def test_jwt_refresh(api_client, create_user):
    """Test refreshing an expired JWT access token."""
    
    _, refresh_token = test_jwt_authentication(api_client, create_user)

    # Step 3: Refresh JWT token
    url = reverse("jwt-refresh")  # Endpoint: /auth/jwt/refresh/
    response = api_client.post(url, {"refresh": refresh_token}, format="json")

    assert response.status_code == 200
    assert "access" in response.data  # New access token is returned


@pytest.mark.django_db
def test_jwt_verify(api_client, create_user):
    """Test verifying a valid JWT access token."""
    
    access_token, _ = test_jwt_authentication(api_client, create_user)

    # Step 4: Verify JWT token
    url = reverse("jwt-verify")  # Endpoint: /auth/jwt/verify/
    response = api_client.post(url, {"token": access_token}, format="json")

    assert response.status_code == 200  # Valid token should return 200 OK


@pytest.mark.django_db
def test_jwt_invalid_token(api_client):
    """Test verifying an invalid JWT token."""
    
    url = reverse("jwt-verify")  # Endpoint: /auth/jwt/verify/
    response = api_client.post(url, {"token": "invalid_token"}, format="json")

    assert response.status_code == 401  # Invalid token should return 401 Unauthorized
    assert response.data["code"] == "token_not_valid"
