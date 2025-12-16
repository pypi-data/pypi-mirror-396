"""Pytest configuration and fixtures."""

import io

import pytest

from just_storage import JustStorageClient


@pytest.fixture
def base_url():
    """Base URL for testing."""
    return "http://localhost:8080"


@pytest.fixture
def api_key():
    """API key for testing."""
    return "test-api-key"


@pytest.fixture
def client(base_url, api_key):
    """JustStorage client fixture."""
    client = JustStorageClient(base_url=base_url, api_key=api_key)
    yield client
    client.close()


@pytest.fixture
def sample_object_data():
    """Sample object data for testing."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "namespace": "test",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "key": "test-file",
        "status": "COMMITTED",
        "storage_class": "hot",
        "content_hash": "sha256:abc123def456",
        "size_bytes": 1024,
        "content_type": "application/octet-stream",
        "metadata": {},
        "created_at": "2025-12-13T10:00:00Z",
        "updated_at": "2025-12-13T10:00:00Z",
    }


@pytest.fixture
def sample_file_data():
    """Sample file data for testing."""
    return b"test file content"


@pytest.fixture
def sample_file_obj(sample_file_data):
    """Sample file object for testing."""
    return io.BytesIO(sample_file_data)


@pytest.fixture
def tenant_id():
    """Sample tenant ID for testing."""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def namespace():
    """Sample namespace for testing."""
    return "test"
