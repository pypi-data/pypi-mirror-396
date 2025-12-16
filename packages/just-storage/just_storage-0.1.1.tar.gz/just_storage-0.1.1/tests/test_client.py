"""Tests for JustStorageClient."""

import io

import pytest

from just_storage import (
    JustStorageClient,
    JustStorageNotFoundError,
    JustStorageUnauthorizedError,
    StorageClass,
)
from just_storage.models import ObjectStatus
from tests.test_utils import (
    MockAPIClient,
    assert_upload_call,
    assert_download_call,
    assert_delete_call,
    assert_list_call,
)


class TestClientInitialization:
    """Test client initialization."""

    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = JustStorageClient(base_url="http://localhost:8080", api_key="test-key")
        assert client.base_url == "http://localhost:8080"
        assert client.session.headers["Authorization"] == "ApiKey test-key"
        client.close()

    def test_init_with_jwt_token(self):
        """Test client initialization with JWT token."""
        client = JustStorageClient(base_url="http://localhost:8080", jwt_token="test-token")
        assert client.session.headers["Authorization"] == "Bearer test-token"
        client.close()

    def test_init_without_auth(self):
        """Test that client requires authentication."""
        with pytest.raises(ValueError, match="Either api_key or jwt_token must be provided"):
            JustStorageClient(base_url="http://localhost:8080")

    def test_init_with_both_auth(self):
        """Test that client rejects both auth methods."""
        with pytest.raises(ValueError, match="Cannot provide both api_key and jwt_token"):
            JustStorageClient(base_url="http://localhost:8080", api_key="key", jwt_token="token")

    def test_context_manager(self):
        """Test context manager usage."""
        with JustStorageClient(base_url="http://localhost:8080", api_key="key") as client:
            assert client.base_url == "http://localhost:8080"


class TestHealth:
    """Test health check methods."""

    def test_health(self, client):
        """Test health check."""
        with MockAPIClient(client) as mock_api:
            mock_api.mock_health()
            status = client.health()

            assert status.status == "healthy"
            assert status.service == "activestorage"
            assert status.version == "0.1.0"

    def test_readiness(self, client):
        """Test readiness check."""
        with MockAPIClient(client) as mock_api:
            mock_api.mock_readiness()
            status = client.readiness()

            assert status.status == "ready"
            assert status.database == "connected"


class TestUpload:
    """Test upload functionality."""

    def test_upload_success(self, client, sample_file_obj, namespace, tenant_id):
        """Test successful upload."""
        with MockAPIClient(client) as mock_api:
            mock_api.mock_upload(namespace=namespace, tenant_id=tenant_id, key="test-file")

            obj = client.upload(
                file_obj=sample_file_obj,
                namespace=namespace,
                tenant_id=tenant_id,
                key="test-file",
                storage_class=StorageClass.HOT,
            )

            assert obj.id == "550e8400-e29b-41d4-a716-446655440000"
            assert obj.namespace == namespace
            assert obj.status == ObjectStatus.COMMITTED
            assert obj.storage_class == StorageClass.HOT
            assert_upload_call(mock_api._mock_request, namespace, tenant_id, "test-file")


class TestDownload:
    """Test download functionality."""

    def test_download_to_file(self, client, tenant_id, sample_file_data):
        """Test download to file."""
        object_id = "550e8400-e29b-41d4-a716-446655440000"

        with MockAPIClient(client) as mock_api:
            mock_api.mock_download(content=sample_file_data, content_hash="sha256:abc123")

            output_file = io.BytesIO()
            obj = client.download(object_id, tenant_id, output_file=output_file)

            assert obj.size_bytes == len(sample_file_data)
            assert obj.content_hash == "sha256:abc123"
            assert output_file.getvalue() == sample_file_data
            assert_download_call(mock_api._mock_request, object_id, tenant_id)

    def test_download_to_memory(self, client, tenant_id, sample_file_data):
        """Test download to memory."""
        object_id = "550e8400-e29b-41d4-a716-446655440000"

        with MockAPIClient(client) as mock_api:
            mock_api.mock_download(content=sample_file_data)

            data = client.download(object_id, tenant_id)

            assert data == sample_file_data
            assert_download_call(mock_api._mock_request, object_id, tenant_id)


class TestDelete:
    """Test delete functionality."""

    def test_delete_success(self, client, tenant_id):
        """Test successful delete."""
        object_id = "550e8400-e29b-41d4-a716-446655440000"

        with MockAPIClient(client) as mock_api:
            mock_api.mock_delete()

            client.delete(object_id, tenant_id)

            assert_delete_call(mock_api._mock_request, object_id, tenant_id)


class TestList:
    """Test list functionality."""

    def test_list_success(self, client, namespace, tenant_id, sample_object_data):
        """Test successful list."""
        with MockAPIClient(client) as mock_api:
            objects = [sample_object_data]
            mock_api.mock_list(objects, total=1, limit=50, offset=0)

            response = client.list(namespace=namespace, tenant_id=tenant_id, limit=50, offset=0)

            assert response.total == 1
            assert len(response.objects) == 1
            assert response.objects[0].id == sample_object_data["id"]
            assert_list_call(mock_api._mock_request, namespace, tenant_id, 50, 0)


class TestErrorHandling:
    """Test error handling."""

    def test_not_found_error(self, client, tenant_id):
        """Test 404 error handling."""
        object_id = "00000000-0000-0000-0000-000000000000"

        with MockAPIClient(client) as mock_api:
            mock_api.mock_not_found("Object not found")

            with pytest.raises(JustStorageNotFoundError):
                client.download(object_id, tenant_id)

    def test_unauthorized_error(self, client, namespace, tenant_id):
        """Test 401 error handling."""
        with MockAPIClient(client) as mock_api:
            mock_api.mock_unauthorized("Unauthorized")

            with pytest.raises(JustStorageUnauthorizedError):
                client.list(namespace, tenant_id)
