import boto3
from moto import mock_s3
import pytest

@mock_s3
def test_create_bucket():
    # Mock S3 environment
    s3 = boto3.client('s3', region_name='us-east-1')
    
    # Create a bucket using Moto
    s3.create_bucket(Bucket='my-test-bucket')
    
    # List buckets to verify
    response = s3.list_buckets()
    bucket_names = [bucket['Name'] for bucket in response['Buckets']]
    
    assert 'my-test-bucket' in bucket_names
