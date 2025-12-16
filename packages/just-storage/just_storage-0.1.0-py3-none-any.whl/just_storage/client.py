"""
Main client for JustStorage SDK.
"""

from typing import BinaryIO, Optional, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from just_storage.exceptions import (
    JustStorageError,
    JustStorageAPIError,
    JustStorageNotFoundError,
    JustStorageUnauthorizedError,
    JustStorageConflictError,
    JustStorageBadRequestError,
)
from just_storage.models import (
    ObjectInfo,
    ListResponse,
    HealthStatus,
    StorageClass,
    ObjectStatus,
)


class JustStorageClient:
    """
    Client for JustStorage API.

    Example:
        ```python
        from just_storage import JustStorageClient

        client = JustStorageClient(
            base_url="http://localhost:8080",
            api_key="your-api-key"
        )

        with open("model.bin", "rb") as f:
            obj = client.upload(
                file_obj=f,
                namespace="models",
                tenant_id="550e8400-e29b-41d4-a716-446655440000",
                key="llama-3.1-8b",
                storage_class=StorageClass.HOT
            )

        with open("downloaded.bin", "wb") as f:
            client.download(obj.id, "550e8400-e29b-41d4-a716-446655440000", f)

        response = client.list(
            namespace="models",
            tenant_id="550e8400-e29b-41d4-a716-446655440000",
            limit=50
        )

        client.delete(obj.id, "550e8400-e29b-41d4-a716-446655440000")
        ```
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize JustStorage client.

        Args:
            base_url: Base URL of the JustStorage service (e.g., "http://localhost:8080")
            api_key: API key for authentication (mutually exclusive with jwt_token)
            jwt_token: JWT bearer token for authentication (mutually exclusive with api_key)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests

        Raises:
            ValueError: If neither api_key nor jwt_token is provided
        """
        if not api_key and not jwt_token:
            raise ValueError("Either api_key or jwt_token must be provided")

        if api_key and jwt_token:
            raise ValueError("Cannot provide both api_key and jwt_token")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set authentication header
        if api_key:
            self.session.headers["Authorization"] = f"ApiKey {api_key}"
        else:
            self.session.headers["Authorization"] = f"Bearer {jwt_token}"

        # Set default headers
        self.session.headers["Content-Type"] = "application/octet-stream"
        self.session.headers["User-Agent"] = "just-storage-python-sdk/0.1.0"

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[Union[bytes, BinaryIO]] = None,
        stream: bool = False,
    ) -> requests.Response:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path (e.g., "/v1/objects")
            params: Query parameters
            data: Request body data
            stream: Whether to stream the response

        Returns:
            Response object

        Raises:
            JustStorageAPIError: For API errors
        """
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                stream=stream,
                timeout=self.timeout,
            )
            self._handle_response(response)
            return response
        except requests.exceptions.RequestException as e:
            raise JustStorageError(f"Request failed: {str(e)}") from e

    def _handle_response(self, response: requests.Response) -> None:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: Response object

        Raises:
            JustStorageAPIError: For API errors
        """
        if response.status_code < 400:
            return

        # Try to parse error response
        try:
            error_data = response.json()
            error_message = error_data.get("error", "Unknown error")
            if isinstance(error_message, dict):
                error_message = error_message.get("message", str(error_message))
        except (ValueError, KeyError):
            error_message = response.text or f"HTTP {response.status_code}"

        # Map status codes to specific exceptions
        if response.status_code == 401:
            raise JustStorageUnauthorizedError(error_message)
        elif response.status_code == 404:
            raise JustStorageNotFoundError(error_message)
        elif response.status_code == 409:
            raise JustStorageConflictError(error_message)
        elif response.status_code == 400:
            raise JustStorageBadRequestError(error_message)
        else:
            raise JustStorageAPIError(
                error_message,
                response.status_code,
            )

    def health(self) -> HealthStatus:
        """
        Check service health.

        Returns:
            HealthStatus object

        Example:
            ```python
            status = client.health()
            print(f"Service status: {status.status}")
            ```
        """
        response = self._request("GET", "/health")
        return HealthStatus.from_dict(response.json())

    def readiness(self) -> HealthStatus:
        """
        Check service readiness (includes database connectivity check).

        Returns:
            HealthStatus object

        Example:
            ```python
            status = client.readiness()
            if status.status == "ready":
                print("Service is ready")
            ```
        """
        response = self._request("GET", "/health/ready")
        return HealthStatus.from_dict(response.json())

    def upload(
        self,
        file_obj: BinaryIO,
        namespace: str,
        tenant_id: str,
        key: Optional[str] = None,
        storage_class: StorageClass = StorageClass.HOT,
    ) -> ObjectInfo:
        """
        Upload an object to storage.

        Args:
            file_obj: File-like object opened in binary mode
            namespace: Object namespace (e.g., 'models', 'kb', 'uploads')
            tenant_id: Tenant identifier (UUID string)
            key: Optional human-readable key for retrieval
            storage_class: Storage class (HOT or COLD)

        Returns:
            ObjectInfo with metadata about the uploaded object

        Raises:
            JustStorageConflictError: If key already exists
            JustStorageAPIError: For other API errors

        Example:
            ```python
            with open("model.bin", "rb") as f:
                obj = client.upload(
                    file_obj=f,
                    namespace="models",
                    tenant_id="550e8400-e29b-41d4-a716-446655440000",
                    key="llama-3.1-8b",
                    storage_class=StorageClass.HOT
                )
            print(f"Uploaded: {obj.id}, Hash: {obj.content_hash}")
            ```
        """
        params = {
            "namespace": namespace,
            "tenant_id": tenant_id,
            "storage_class": storage_class.value,
        }
        if key:
            params["key"] = key

        response = self._request("POST", "/v1/objects", params=params, data=file_obj)
        return ObjectInfo.from_dict(response.json())

    def download(
        self,
        object_id: str,
        tenant_id: str,
        output_file: Optional[BinaryIO] = None,
        verify_hash: bool = False,
    ) -> Union[bytes, ObjectInfo]:
        """
        Download an object by ID.

        Args:
            object_id: Object UUID
            tenant_id: Tenant identifier (UUID string)
            output_file: Optional file-like object to write to. If None, returns bytes.
            verify_hash: If True, verify content hash matches (requires reading into memory)

        Returns:
            If output_file is None, returns bytes. Otherwise returns ObjectInfo with metadata.

        Raises:
            JustStorageNotFoundError: If object doesn't exist
            JustStorageAPIError: For other API errors

        Example:
            ```python
            # Download to file
            with open("downloaded.bin", "wb") as f:
                obj = client.download(
                    "550e8400-e29b-41d4-a716-446655440000",
                    "550e8400-e29b-41d4-a716-446655440000",
                    output_file=f
                )

            # Download to memory
            data = client.download(
                "550e8400-e29b-41d4-a716-446655440000",
                "550e8400-e29b-41d4-a716-446655440000"
            )
            ```
        """
        params = {"tenant_id": tenant_id}
        response = self._request("GET", f"/v1/objects/{object_id}", params=params, stream=True)

        # Extract metadata from headers
        content_hash = response.headers.get("X-Content-Hash", "")
        size_bytes = int(response.headers.get("Content-Length", 0))

        if output_file:
            # Stream to file
            for chunk in response.iter_content(chunk_size=8192):
                output_file.write(chunk)
            # Return minimal metadata
            return ObjectInfo(
                id=object_id,
                namespace="",  # Not available in headers
                tenant_id=tenant_id,
                key=None,
                status=ObjectStatus.COMMITTED,
                storage_class=StorageClass.HOT,  # Not available in headers
                content_hash=content_hash,
                size_bytes=size_bytes,
                content_type=response.headers.get("Content-Type"),
                metadata={},
                created_at=None,  # type: ignore
                updated_at=None,  # type: ignore
            )
        else:
            # Read into memory
            data = response.content
            if verify_hash and content_hash:
                from just_storage.utils import verify_content_hash

                if not verify_content_hash(data, content_hash):
                    raise JustStorageError("Content hash verification failed")

            return data

    def delete(self, object_id: str, tenant_id: str) -> None:
        """
        Delete an object.

        Args:
            object_id: Object UUID
            tenant_id: Tenant identifier (UUID string)

        Raises:
            JustStorageNotFoundError: If object doesn't exist
            JustStorageAPIError: For other API errors

        Example:
            ```python
            client.delete(
                "550e8400-e29b-41d4-a716-446655440000",
                "550e8400-e29b-41d4-a716-446655440000"
            )
            ```
        """
        params = {"tenant_id": tenant_id}
        self._request("DELETE", f"/v1/objects/{object_id}", params=params)

    def list(
        self,
        namespace: str,
        tenant_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> ListResponse:
        """
        List objects with pagination.

        Args:
            namespace: Filter by namespace
            tenant_id: Filter by tenant
            limit: Results per page (default: 50, max: 1000)
            offset: Pagination offset (default: 0)

        Returns:
            ListResponse with objects and pagination info

        Raises:
            JustStorageAPIError: For API errors

        Example:
            ```python
            response = client.list(
                namespace="models",
                tenant_id="550e8400-e29b-41d4-a716-446655440000",
                limit=50,
                offset=0
            )
            print(f"Total: {response.total}, Showing: {len(response.objects)}")
            for obj in response.objects:
                print(f"  {obj.id}: {obj.key} ({obj.size_bytes} bytes)")
            ```
        """
        params = {
            "namespace": namespace,
            "tenant_id": tenant_id,
            "limit": limit,
            "offset": offset,
        }
        response = self._request("GET", "/v1/objects", params=params)
        return ListResponse.from_dict(response.json())

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
