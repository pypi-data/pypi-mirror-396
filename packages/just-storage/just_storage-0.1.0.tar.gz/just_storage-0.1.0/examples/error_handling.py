"""
Error handling examples for JustStorage Python SDK.
"""

from just_storage import (
    JustStorageClient,
    JustStorageError,
    JustStorageAPIError,
    JustStorageNotFoundError,
    JustStorageUnauthorizedError,
    JustStorageConflictError,
    StorageClass,
)

client = JustStorageClient(base_url="http://localhost:8080", api_key="askh48y2h3hasf@#$")

# Example 1: Handle not found error
print("Example 1: Handling not found error")
try:
    client.download("00000000-0000-0000-0000-000000000000", "550e8400-e29b-41d4-a716-446655440000")
except JustStorageNotFoundError as e:
    print(f"Object not found: {e.message}")
except JustStorageAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")

# Example 2: Handle conflict error (duplicate key)
print("\nExample 2: Handling conflict error")
try:
    with open("test_file.txt", "rb") as f:
        # First upload
        obj1 = client.upload(
            file_obj=f,
            namespace="test",
            tenant_id="550e8400-e29b-41d4-a716-446655440000",
            key="duplicate-key",
            storage_class=StorageClass.HOT,
        )
        print(f"First upload: {obj1.id}")

    with open("test_file.txt", "rb") as f:
        # Second upload with same key (should fail)
        obj2 = client.upload(
            file_obj=f,
            namespace="test",
            tenant_id="550e8400-e29b-41d4-a716-446655440000",
            key="duplicate-key",
            storage_class=StorageClass.HOT,
        )
except JustStorageConflictError as e:
    print(f"Conflict: {e.message}")
    if e.details:
        print(f"Details: {e.details}")

# Example 3: Handle unauthorized error
print("\nExample 3: Handling unauthorized error")
unauthorized_client = JustStorageClient(base_url="http://localhost:8080", api_key="invalid-key")
try:
    unauthorized_client.list(namespace="test", tenant_id="550e8400-e29b-41d4-a716-446655440000")
except JustStorageUnauthorizedError as e:
    print(f"Unauthorized: {e.message}")

# Example 4: Generic error handling
print("\nExample 4: Generic error handling")
try:
    # Some operation that might fail
    client.upload(
        file_obj=open("nonexistent.txt", "rb"),
        namespace="test",
        tenant_id="550e8400-e29b-41d4-a716-446655440000",
    )
except JustStorageNotFoundError:
    print("Not found")
except JustStorageUnauthorizedError:
    print("Unauthorized")
except JustStorageConflictError:
    print("Conflict")
except JustStorageAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
except JustStorageError as e:
    print(f"Error: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")

client.close()
