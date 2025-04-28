#!/usr/bin/env python
"""
Test script for s3sim with all the new features.
"""

import os
import json
import tempfile
import shutil
import subprocess
import time
from s3sim.s3_operations import (
    create_bucket,
    delete_bucket,
    list_buckets,
    upload_file,
    read_file,
    delete_file,
    list_files,
    upload_large_file,
    get_object_metadata,
    load_config_from_file,
    get_s3_client,
    permission_manager
)

def start_moto_server():
    """Start moto server for testing."""
    print("Starting Moto server...")
    process = subprocess.Popen(
        ["moto_server", "-p", "5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait for server to start
    time.sleep(2)
    return process

def stop_moto_server(process):
    """Stop moto server."""
    print("Stopping Moto server...")
    process.terminate()
    process.wait()

def test_configuration_loading():
    """Test loading configuration from file."""
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({
            "endpoint_url": "http://localhost:5000",
            "region": "us-west-2"
        }, f)
        config_path = f.name
    
    # Load config
    config = load_config_from_file(config_path)
    
    # Verify config loaded correctly
    assert "endpoint_url" in config
    assert os.environ.get("S3_ENDPOINT_URL") == "http://localhost:5000"
    
    # Clean up
    os.unlink(config_path)
    print("✓ Configuration loading test passed")

def test_bucket_operations(user_id="test_user"):
    """Test basic bucket operations."""
    # Create bucket
    bucket_name = "test-bucket"
    assert create_bucket(bucket_name, user_id=user_id)
    
    # List buckets
    buckets = list_buckets()
    assert bucket_name in buckets
    
    # Verify permissions
    assert permission_manager.check_bucket_permission(bucket_name, user_id, "read")
    assert permission_manager.check_bucket_permission(bucket_name, user_id, "write")
    assert permission_manager.check_bucket_permission(bucket_name, user_id, "delete")
    
    # Delete bucket
    assert delete_bucket(bucket_name, force=True, user_id=user_id)
    
    # Verify bucket deletion
    buckets = list_buckets()
    assert bucket_name not in buckets
    
    print("✓ Bucket operations test passed")

def test_file_operations_with_metadata(user_id="test_user"):
    """Test file operations with metadata."""
    # Create bucket
    bucket_name = "test-file-bucket"
    assert create_bucket(bucket_name, user_id=user_id)
    
    # Upload file with metadata
    key = "test-file.txt"
    content = "Hello, world!"
    metadata = {"author": "Test User", "version": "1.0"}
    assert upload_file(bucket_name, key, content, user_id=user_id, metadata=metadata)
    
    # Read file
    retrieved_content = read_file(bucket_name, key, user_id=user_id)
    assert retrieved_content == content
    
    # Verify metadata
    retrieved_metadata = get_object_metadata(bucket_name, key, user_id=user_id)
    assert "author" in retrieved_metadata
    assert retrieved_metadata["author"] == "Test User"
    
    # List files
    files = list_files(bucket_name, user_id=user_id)
    assert key in files
    
    # Delete file
    assert delete_file(bucket_name, key, user_id=user_id)
    
    # Clean up
    delete_bucket(bucket_name, force=True)
    
    print("✓ File operations with metadata test passed")

def test_multipart_upload(user_id="test_user"):
    """Test multipart upload for large files."""
    # Create bucket
    bucket_name = "test-multipart-bucket"
    assert create_bucket(bucket_name, user_id=user_id)
    
    # Create a temporary large file
    temp_dir = tempfile.mkdtemp()
    try:
        large_file_path = os.path.join(temp_dir, "large_file.bin")
        
        # Create a 10MB file
        with open(large_file_path, 'wb') as f:
            f.write(b'0' * 10 * 1024 * 1024)  # 10MB of zeros
        
        # Upload using multipart
        key = "large-file.bin"
        metadata = {"content-type": "application/octet-stream"}
        assert upload_large_file(
            bucket_name, 
            key, 
            large_file_path, 
            user_id=user_id,
            part_size=1*1024*1024,  # 1MB parts
            metadata=metadata
        )
        
        # Verify file exists
        files = list_files(bucket_name, user_id=user_id)
        assert key in files
        
        # Check metadata
        retrieved_metadata = get_object_metadata(bucket_name, key, user_id=user_id)
        assert "content-type" in retrieved_metadata
        
        # Clean up
        delete_file(bucket_name, key, user_id=user_id)
        delete_bucket(bucket_name, force=True)
        
    finally:
        # Clean up temp dir
        shutil.rmtree(temp_dir)
    
    print("✓ Multipart upload test passed")

def test_permission_controls():
    """Test permission controls."""
    # Create bucket with user1
    bucket_name = "permission-test-bucket"
    user1 = "user1"
    user2 = "user2"
    
    assert create_bucket(bucket_name, user_id=user1)
    
    # Upload file as user1
    key = "secret.txt"
    content = "This is a secret"
    assert upload_file(bucket_name, key, content, user_id=user1)
    
    # Try to read as user2 (should fail)
    try:
        read_file(bucket_name, key, user_id=user2)
        assert False, "User2 shouldn't be able to read user1's file"
    except Exception:
        pass  # Expected to fail
    
    # Grant read permission to user2
    permission_manager.add_object_permission(bucket_name, key, user2, "read")
    
    # Now user2 should be able to read
    assert read_file(bucket_name, key, user_id=user2) == content
    
    # But user2 still can't write
    try:
        upload_file(bucket_name, key, "Modified content", user_id=user2)
        assert False, "User2 shouldn't be able to write to user1's file"
    except Exception:
        pass  # Expected to fail
    
    # Clean up
    delete_bucket(bucket_name, force=True, user_id=user1)
    
    print("✓ Permission controls test passed")

def run_all_tests():
    """Run all tests."""
    moto_process = start_moto_server()
    
    try:
        # Set endpoint URL for all tests
        os.environ["S3_ENDPOINT_URL"] = "http://localhost:5000"
        
        print("\n=== Running S3Sim Tests ===\n")
        
        # Run tests
        test_configuration_loading()
        test_bucket_operations()
        test_file_operations_with_metadata()
        test_multipart_upload()
        test_permission_controls()
        
        print("\n=== All Tests Passed! ===\n")
    finally:
        stop_moto_server(moto_process)

if __name__ == "__main__":
    run_all_tests()