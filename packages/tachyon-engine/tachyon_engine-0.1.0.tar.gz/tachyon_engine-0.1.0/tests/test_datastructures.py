"""
Tests for data structures (Headers, QueryParams, etc.)
"""

import pytest
from tachyon_engine import Headers, QueryParams, UploadFile


def test_headers_creation():
    """Test creating Headers instance"""
    headers = Headers()
    assert headers is not None


def test_headers_set_get():
    """Test setting and getting headers"""
    headers = Headers()
    headers.set("Content-Type", "application/json")
    
    assert headers.get("Content-Type") == "application/json"
    assert headers.get("content-type") == "application/json"  # Case-insensitive


def test_headers_contains():
    """Test checking if header exists"""
    headers = Headers()
    headers.set("Authorization", "Bearer token123")
    
    assert headers.contains("Authorization")
    assert headers.contains("authorization")
    assert not headers.contains("X-Custom-Header")


def test_query_params_creation():
    """Test creating QueryParams instance"""
    params = QueryParams()
    assert params is not None


def test_upload_file_creation():
    """Test creating UploadFile instance"""
    file = UploadFile(
        filename="test.txt",
        content_type="text/plain",
        content=b"Hello, World!",
    )
    
    assert file.filename == "test.txt"
    assert file.content_type == "text/plain"
    assert file.size == 13


def test_upload_file_read():
    """Test reading from UploadFile"""
    content = b"Test content"
    file = UploadFile(
        filename="test.txt",
        content_type="text/plain",
        content=content,
    )
    
    data = file.read()
    assert data == content


def test_upload_file_seek():
    """Test seeking in UploadFile"""
    file = UploadFile(
        filename="test.txt",
        content_type="text/plain",
        content=b"Hello, World!",
    )
    
    file.seek(7)
    # After seeking, next read should start from position 7
    # (Implementation dependent)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

