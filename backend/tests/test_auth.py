"""Tests for authentication"""
import pytest
from app.models.user import User, UserRole
from app.auth import get_password_hash


def test_login_success(client, db_session):
    """Test successful login"""
    # Create user
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.SALES_ENGINEER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client, db_session):
    """Test login with invalid credentials"""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401


def test_login_inactive_user(client, db_session):
    """Test login with inactive user"""
    user = User(
        email="inactive@example.com",
        full_name="Inactive User",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.CUSTOMER,
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post("/auth/login", json={
        "email": "inactive@example.com",
        "password": "testpass123"
    })
    
    assert response.status_code == 403


def test_get_current_user(client, db_session):
    """Test getting current user info"""
    # Create and login user
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.ADMINISTRATOR,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "administrator"


def test_unauthorized_access(client):
    """Test accessing protected endpoint without token"""
    response = client.get("/auth/me")
    assert response.status_code == 403  # No Authorization header


def test_invalid_token(client):
    """Test accessing with invalid token"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
