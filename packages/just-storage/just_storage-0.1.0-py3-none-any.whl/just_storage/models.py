"""
Data models for JustStorage SDK.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class StorageClass(str, Enum):
    """Storage class for objects."""

    HOT = "hot"
    COLD = "cold"


class ObjectStatus(str, Enum):
    """Object status in the state machine."""

    WRITING = "WRITING"
    COMMITTED = "COMMITTED"
    DELETING = "DELETING"
    DELETED = "DELETED"


@dataclass
class ObjectInfo:
    """Metadata about a stored object."""

    id: str
    namespace: str
    tenant_id: str
    key: Optional[str]
    status: ObjectStatus
    storage_class: StorageClass
    content_hash: Optional[str]
    size_bytes: Optional[int]
    content_type: Optional[str]
    metadata: Dict[str, Any]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObjectInfo":
        """Create ObjectInfo from API response dictionary."""
        # Parse datetime strings
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))

        return cls(
            id=data["id"],
            namespace=data["namespace"],
            tenant_id=data["tenant_id"],
            key=data.get("key"),
            status=ObjectStatus(data["status"]),
            storage_class=StorageClass(data["storage_class"]),
            content_hash=data.get("content_hash"),
            size_bytes=data.get("size_bytes"),
            content_type=data.get("content_type"),
            metadata=data.get("metadata", {}),
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class ListResponse:
    """Response from list objects endpoint."""

    objects: list[ObjectInfo]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListResponse":
        """Create ListResponse from API response dictionary."""
        return cls(
            objects=[ObjectInfo.from_dict(obj) for obj in data["objects"]],
            total=data["total"],
            limit=data["limit"],
            offset=data["offset"],
        )


@dataclass
class HealthStatus:
    """Health check response."""

    status: str
    service: str
    version: Optional[str] = None
    database: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthStatus":
        """Create HealthStatus from API response dictionary."""
        return cls(
            status=data["status"],
            service=data.get("service", "activestorage"),
            version=data.get("version"),
            database=data.get("database"),
        )
