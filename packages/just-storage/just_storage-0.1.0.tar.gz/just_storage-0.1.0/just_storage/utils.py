"""
Utility functions for JustStorage SDK.
"""

import hashlib
from typing import BinaryIO, Iterator, Optional


def calculate_sha256(file_obj: BinaryIO) -> str:
    """
    Calculate SHA-256 hash of a file.

    Args:
        file_obj: File-like object opened in binary mode

    Returns:
        Hex-encoded SHA-256 hash
    """
    sha256 = hashlib.sha256()
    file_obj.seek(0)  # Reset to beginning
    for chunk in iter(lambda: file_obj.read(8192), b""):
        sha256.update(chunk)
    file_obj.seek(0)  # Reset again for use
    return sha256.hexdigest()


def verify_content_hash(data: bytes, expected_hash: str) -> bool:
    """
    Verify that data matches the expected content hash.

    Args:
        data: Binary data to verify
        expected_hash: Expected SHA-256 hash (hex-encoded, with or without 'sha256:' prefix)

    Returns:
        True if hash matches, False otherwise
    """
    # Remove 'sha256:' prefix if present
    hash_value = expected_hash.replace("sha256:", "")
    actual_hash = hashlib.sha256(data).hexdigest()
    return actual_hash.lower() == hash_value.lower()


def chunk_file(file_obj: BinaryIO, chunk_size: int = 8192) -> Iterator[bytes]:
    """
    Read file in chunks.

    Args:
        file_obj: File-like object opened in binary mode
        chunk_size: Size of each chunk in bytes

    Yields:
        Chunks of file data
    """
    file_obj.seek(0)
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk
    file_obj.seek(0)


def format_size(size_bytes: Optional[int]) -> str:
    """
    Format size in bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string (e.g., "1.5 MB")
    """
    if size_bytes is None:
        return "Unknown"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
