"""Test configuration"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app
from app.config import settings

# Test database URL
TEST_DATABASE_URL = settings.DATABASE_TEST_URL

# Create test engine
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for a test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a test database session"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def platform_admin_token(client, db_session):
    """Create a platform admin user and return auth token"""
    from app.models.user import User, UserRole
    from app.auth import get_password_hash
    
    user = User(
        email="admin@platform.com",
        full_name="Platform Admin",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post("/auth/login", json={
        "email": "admin@platform.com",
        "password": "testpass123"
    })
    return response.json()["access_token"]


@pytest.fixture
def tenant_admin_token(client, db_session):
    """Create a tenant admin user and return auth token"""
    from app.models.user import User, UserRole
    from app.models.tenant import Tenant
    from app.auth import get_password_hash
    
    # Create tenant
    tenant = Tenant(
        name="Test Tenant",
        subdomain="test",
    )
    db_session.add(tenant)
    db_session.commit()
    
    # Create tenant admin
    user = User(
        email="admin@tenant.com",
        full_name="Tenant Admin",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.TENANT_ADMIN,
        tenant_id=tenant.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post("/auth/login", json={
        "email": "admin@tenant.com",
        "password": "testpass123"
    })
    return response.json()["access_token"]
