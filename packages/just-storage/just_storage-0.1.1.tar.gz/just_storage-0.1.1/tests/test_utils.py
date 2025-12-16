"""Test utilities and mock helpers."""

import io
from typing import Optional, Dict, Any

import requests


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        content: Optional[bytes] = None,
        text: str = "",
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self._json_data = json_data or {}
        self._content = content or b""
        self._text = text
        self.headers = headers or {}
        self.url = "http://localhost:8080"

    def json(self):
        """Return JSON data."""
        return self._json_data

    @property
    def content(self):
        """Return content."""
        return self._content

    @property
    def text(self):
        """Return text."""
        return self._text

    def iter_content(self, chunk_size: int = 8192):
        """Iterate over content in chunks."""
        data = self._content
        for i in range(0, len(data), chunk_size):
            yield data[i : i + chunk_size]

    def raise_for_status(self):
        """Raise HTTPError for bad status codes."""
        if 400 <= self.status_code < 600:
            raise requests.HTTPError(response=self)


class APIResponseBuilder:
    """Builder for creating API response mocks."""

    @staticmethod
    def health_response(status: str = "healthy") -> Dict[str, Any]:
        """Build health check response."""
        return {"status": status, "service": "activestorage", "version": "0.1.0"}

    @staticmethod
    def readiness_response(status: str = "ready", database: str = "connected") -> Dict[str, Any]:
        """Build readiness check response."""
        return {"status": status, "service": "activestorage", "database": database}

    @staticmethod
    def object_response(
        object_id: str = "550e8400-e29b-41d4-a716-446655440000",
        namespace: str = "test",
        tenant_id: str = "550e8400-e29b-41d4-a716-446655440000",
        key: Optional[str] = "test-file",
        status: str = "COMMITTED",
        storage_class: str = "hot",
        content_hash: Optional[str] = "sha256:abc123",
        size_bytes: Optional[int] = 1024,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build object response."""
        return {
            "id": object_id,
            "namespace": namespace,
            "tenant_id": tenant_id,
            "key": key,
            "status": status,
            "storage_class": storage_class,
            "content_hash": content_hash,
            "size_bytes": size_bytes,
            "content_type": content_type,
            "metadata": metadata or {},
            "created_at": "2025-12-13T10:00:00Z",
            "updated_at": "2025-12-13T10:00:00Z",
        }

    @staticmethod
    def list_response(
        objects: list[Dict[str, Any]],
        total: int,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Build list response."""
        return {"objects": objects, "total": total, "limit": limit, "offset": offset}

    @staticmethod
    def error_response(
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build error response."""
        return {
            "error": message,
            "code": error_code or f"ERROR_{status_code}",
        }


class MockAPIClient:
    """Helper for mocking API client requests."""

    def __init__(self, client):
        """Initialize with a JustStorageClient instance."""
        self.client = client
        self._request_patcher = None

    def __enter__(self):
        """Context manager entry."""
        from unittest.mock import patch

        self._request_patcher = patch.object(self.client, "_request")
        self._mock_request = self._request_patcher.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._request_patcher:
            self._request_patcher.__exit__(exc_type, exc_val, exc_tb)

    def mock_health(self, status: str = "healthy"):
        """Mock health endpoint."""
        response = MockResponse(json_data=APIResponseBuilder.health_response(status))
        self._mock_request.return_value = response
        return response

    def mock_readiness(self, status: str = "ready", database: str = "connected"):
        """Mock readiness endpoint."""
        response = MockResponse(json_data=APIResponseBuilder.readiness_response(status, database))
        self._mock_request.return_value = response
        return response

    def mock_upload(self, **kwargs):
        """Mock upload endpoint."""
        response = MockResponse(
            status_code=201, json_data=APIResponseBuilder.object_response(**kwargs)
        )
        self._mock_request.return_value = response
        return response

    def mock_download(
        self,
        content: bytes = b"test data",
        content_hash: str = "sha256:abc123",
        content_type: str = "application/octet-stream",
    ):
        """Mock download endpoint."""
        response = MockResponse(
            content=content,
            headers={
                "Content-Length": str(len(content)),
                "Content-Type": content_type,
                "X-Content-Hash": content_hash,
            },
        )
        self._mock_request.return_value = response
        return response

    def mock_delete(self, status_code: int = 204):
        """Mock delete endpoint."""
        response = MockResponse(status_code=status_code)
        self._mock_request.return_value = response
        return response

    def mock_list(
        self, objects: list[Dict[str, Any]], total: int, limit: int = 50, offset: int = 0
    ):
        """Mock list endpoint."""
        response = MockResponse(
            json_data=APIResponseBuilder.list_response(objects, total, limit, offset)
        )
        self._mock_request.return_value = response
        return response

    def mock_error(self, message: str, status_code: int = 400, error_code: Optional[str] = None):
        """Mock error response."""
        response = MockResponse(
            status_code=status_code,
            json_data=APIResponseBuilder.error_response(message, status_code, error_code),
            text=message,
        )
        self._mock_request.return_value = response
        return response

    def mock_not_found(self, message: str = "Object not found"):
        """Mock 404 response."""
        response = MockResponse(status_code=404, json_data={"error": message}, text=message)

        # Make _request return response that triggers error handling
        def side_effect(*args, **kwargs):
            # _request calls _handle_response which checks status_code
            self.client._handle_response(response)
            return response

        self._mock_request.side_effect = side_effect
        return response

    def mock_unauthorized(self, message: str = "Unauthorized"):
        """Mock 401 response."""
        response = MockResponse(status_code=401, json_data={"error": message}, text=message)

        # Make _request return response that triggers error handling
        def side_effect(*args, **kwargs):
            self.client._handle_response(response)
            return response

        self._mock_request.side_effect = side_effect
        return response

    def mock_conflict(self, message: str = "Conflict", details: Optional[str] = None):
        """Mock 409 response."""
        return self.mock_error(message, 409, "CONFLICT")

    def mock_bad_request(self, message: str = "Bad request"):
        """Mock 400 response."""
        return self.mock_error(message, 400, "BAD_REQUEST")


def create_mock_file(content: bytes = b"test data") -> io.BytesIO:
    """Create a mock file object."""
    return io.BytesIO(content)


def assert_upload_call(mock_request, namespace: str, tenant_id: str, key: Optional[str] = None):
    """Assert upload was called with correct parameters."""
    assert mock_request.called
    call_args = mock_request.call_args
    assert call_args[0][0] == "POST"
    assert call_args[0][1] == "/v1/objects"

    params = call_args[1]["params"]
    assert params["namespace"] == namespace
    assert params["tenant_id"] == tenant_id
    if key:
        assert params["key"] == key


def assert_download_call(mock_request, object_id: str, tenant_id: str):
    """Assert download was called with correct parameters."""
    assert mock_request.called
    call_args = mock_request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == f"/v1/objects/{object_id}"
    assert call_args[1]["params"]["tenant_id"] == tenant_id
    assert call_args[1]["stream"] is True


def assert_delete_call(mock_request, object_id: str, tenant_id: str):
    """Assert delete was called with correct parameters."""
    assert mock_request.called
    call_args = mock_request.call_args
    assert call_args[0][0] == "DELETE"
    assert call_args[0][1] == f"/v1/objects/{object_id}"
    assert call_args[1]["params"]["tenant_id"] == tenant_id


def assert_list_call(
    mock_request, namespace: str, tenant_id: str, limit: int = 50, offset: int = 0
):
    """Assert list was called with correct parameters."""
    assert mock_request.called
    call_args = mock_request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "/v1/objects"

    params = call_args[1]["params"]
    assert params["namespace"] == namespace
    assert params["tenant_id"] == tenant_id
    assert params["limit"] == limit
    assert params["offset"] == offset
