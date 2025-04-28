"""
Tests for S3 operations module.
"""

import pytest
from moto import mock_aws
import os
import boto3
from botocore.exceptions import ClientError

from s3sim.s3_operations import (
    create_bucket, bucket_exists, list_buckets, upload_file, 
    read_file, update_file, delete_file, list_files, delete_bucket
)

@pytest.fixture
def aws_credentials():
    """Mock AWS credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def s3_mock(aws_credentials):
    """Create mock S3 service."""
    with mock_aws():
        yield

class TestS3Operations:
    """Test S3 operations with moto."""
    
    def test_create_bucket(self, s3_mock):
        """Test bucket creation."""
        assert create_bucket('test-bucket')
        assert bucket_exists('test-bucket')
    
    def test_create_bucket_with_region(self, s3_mock):
        """Test bucket creation with specific region."""
        assert create_bucket('test-bucket-west', region='us-west-1')
        assert bucket_exists('test-bucket-west')
    
    def test_list_buckets(self, s3_mock):
        """Test listing buckets."""
        create_bucket('bucket1')
        create_bucket('bucket2')
        buckets = list_buckets()
        assert len(buckets) == 2
        assert 'bucket1' in buckets
        assert 'bucket2' in buckets
    
    def test_upload_and_read_file(self, s3_mock):
        """Test file upload and read."""
        create_bucket('test-bucket')
        content = "Hello, world!"
        
        # Test string content
        assert upload_file('test-bucket', 'test.txt', content)
        assert read_file('test-bucket', 'test.txt') == content
        
        # Test binary content
        binary_content = b"Binary data"
        assert upload_file('test-bucket', 'binary.bin', binary_content)
        # When reading binary file, it gets decoded to UTF-8
        assert read_file('test-bucket', 'binary.bin') == binary_content.decode('utf-8')
    
    def test_read_nonexistent_file(self, s3_mock):
        """Test reading a file that doesn't exist."""
        create_bucket('test-bucket')
        
        with pytest.raises(Exception):
            read_file('test-bucket', 'nonexistent.txt')
    
    def test_update_file(self, s3_mock):
        """Test file update."""
        create_bucket('test-bucket')
        
        # Upload initial content
        upload_file('test-bucket', 'update.txt', 'Initial content')
        assert read_file('test-bucket', 'update.txt') == 'Initial content'
        
        # Update content
        assert update_file('test-bucket', 'update.txt', 'Updated content')
        assert read_file('test-bucket', 'update.txt') == 'Updated content'
    
    def test_delete_file(self, s3_mock):
        """Test file deletion."""
        create_bucket('test-bucket')
        upload_file('test-bucket', 'delete.txt', 'To be deleted')
        
        # Confirm file exists
        assert read_file('test-bucket', 'delete.txt') == 'To be deleted'
        
        # Delete file
        assert delete_file('test-bucket', 'delete.txt')
        
        # Confirm file is gone
        with pytest.raises(Exception):
            read_file('test-bucket', 'delete.txt')
    
    def test_list_files(self, s3_mock):
        """Test listing files."""
        create_bucket('test-bucket')
        
        # Upload some files
        upload_file('test-bucket', 'file1.txt', 'Content 1')
        upload_file('test-bucket', 'file2.txt', 'Content 2')
        upload_file('test-bucket', 'subdir/file3.txt', 'Content 3')
        
        # List all files
        all_files = list_files('test-bucket')
        assert len(all_files) == 3
        assert 'file1.txt' in all_files
        
        # List files with prefix
        subdir_files = list_files('test-bucket', prefix='subdir/')
        assert len(subdir_files) == 1
        assert subdir_files[0] == 'subdir/file3.txt'
    
    def test_delete_bucket(self, s3_mock):
        """Test bucket deletion."""
        create_bucket('test-bucket')
        
        # Empty bucket can be deleted
        assert delete_bucket('test-bucket')
        assert not bucket_exists('test-bucket')
        
        # Test force deletion of non-empty bucket
        create_bucket('test-bucket')
        upload_file('test-bucket', 'file1.txt', 'Content')
        
        # Should delete bucket and its contents
        assert delete_bucket('test-bucket', force=True)
        assert not bucket_exists('test-bucket')