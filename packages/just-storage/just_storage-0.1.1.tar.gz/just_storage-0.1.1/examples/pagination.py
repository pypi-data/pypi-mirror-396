"""
Pagination examples for JustStorage Python SDK.
"""

from just_storage import JustStorageClient

client = JustStorageClient(base_url="http://localhost:8080", api_key="askh48y2h3hasf@#$")

namespace = "models"
tenant_id = "550e8400-e29b-41d4-a716-446655440000"

# Method 1: Iterate through all pages
print("Iterating through all pages...")
offset = 0
limit = 10
total_objects = 0

while True:
    response = client.list(namespace=namespace, tenant_id=tenant_id, limit=limit, offset=offset)

    print(f"Page {offset // limit + 1}: {len(response.objects)} objects")
    for obj in response.objects:
        print(f"  - {obj.id}: {obj.key}")
        total_objects += 1

    if offset + limit >= response.total:
        break

    offset += limit

print(f"\nTotal objects processed: {total_objects}")

# Method 2: Get specific page
print("\nGetting page 2...")
response = client.list(namespace=namespace, tenant_id=tenant_id, limit=10, offset=10)
print(f"Page 2: {len(response.objects)} objects")
print(f"Total: {response.total}, Limit: {response.limit}, Offset: {response.offset}")

client.close()
