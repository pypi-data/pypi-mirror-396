"""
Basic usage examples for JustStorage Python SDK.
"""

from just_storage import JustStorageClient, StorageClass

# Initialize client
client = JustStorageClient(base_url="http://localhost:8080", api_key="askh48y2h3hasf@#$")

# Check health
print("Checking health...")
health = client.health()
print(f"Service status: {health.status}")

# Upload a file
print("\nUploading file...")
with open("test_file.txt", "rb") as f:
    obj = client.upload(
        file_obj=f,
        namespace="test",
        tenant_id="550e8400-e29b-41d4-a716-446655440000",
        key="test-file.txt",
        storage_class=StorageClass.HOT,
    )
print(f"Uploaded: {obj.id}")
print(f"Content hash: {obj.content_hash}")
print(f"Size: {obj.size_bytes} bytes")

# Download to file
print("\nDownloading to file...")
with open("downloaded.txt", "wb") as f:
    downloaded_obj = client.download(obj.id, "550e8400-e29b-41d4-a716-446655440000", output_file=f)
print(f"Downloaded: {downloaded_obj.size_bytes} bytes")

# Download to memory
print("\nDownloading to memory...")
data = client.download(obj.id, "550e8400-e29b-41d4-a716-446655440000")
print(f"Downloaded: {len(data)} bytes")
print(f"Content: {data.decode('utf-8')}")

# List objects
print("\nListing objects...")
response = client.list(namespace="test", tenant_id="550e8400-e29b-41d4-a716-446655440000", limit=50)
print(f"Total objects: {response.total}")
for obj in response.objects:
    print(f"  - {obj.id}: {obj.key} ({obj.size_bytes} bytes)")

# Delete object
print("\nDeleting object...")
client.delete(obj.id, "550e8400-e29b-41d4-a716-446655440000")
print("Deleted successfully")

# Cleanup
client.close()
