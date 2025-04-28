"""
S3 Operations Module

This module provides CRUD operations for AWS S3, configurable to work with either
real AWS S3 or the Moto S3 simulator via an endpoint URL environment variable.
"""

import boto3
import os
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_s3_client():
    """
    Create and return an S3 client configured based on environment variables.
    
    Returns:
        boto3.client: Configured S3 client
    """
    # Get endpoint URL from environment variable (None for real S3)
    endpoint_url = os.environ.get('S3_ENDPOINT_URL', None)
    
    # Create S3 client with optional endpoint URL
    return boto3.client('s3', endpoint_url=endpoint_url)

def create_bucket(bucket_name, region=None):
    """
    Create an S3 bucket.
    
    Args:
        bucket_name (str): Name of the bucket to create
        region (str, optional): AWS region for the bucket
    
    Returns:
        bool: True if bucket created successfully, False otherwise
    """
    s3_client = get_s3_client()
    
    try:
        # Different approach needed depending on if we're using Moto or real AWS
        if os.environ.get('S3_ENDPOINT_URL'):
            # Simplified for Moto
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            # For real AWS, handle region configuration
            if region is None:
                region = 'us-east-1'  # Default region
                
            if region == 'us-east-1':
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                location = {'LocationConstraint': region}
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration=location
                )
        
        logger.info(f"Bucket '{bucket_name}' created successfully")
        return True
    
    except ClientError as e:
        logger.error(f"Error creating bucket '{bucket_name}': {e}")
        return False

def bucket_exists(bucket_name):
    """
    Check if a bucket exists.
    
    Args:
        bucket_name (str): Name of the bucket to check
    
    Returns:
        bool: True if bucket exists, False otherwise
    """
    s3_client = get_s3_client()
    
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False

def list_buckets():
    """
    List all S3 buckets.
    
    Returns:
        list: List of bucket names
    """
    s3_client = get_s3_client()
    
    try:
        response = s3_client.list_buckets()
        return [bucket['Name'] for bucket in response['Buckets']]
    
    except ClientError as e:
        logger.error(f"Error listing buckets: {e}")
        return []

def upload_file(bucket_name, key, content):
    """
    Upload content to an S3 object.
    
    Args:
        bucket_name (str): Target bucket name
        key (str): Object key (path)
        content (str or bytes): Content to upload
    
    Returns:
        bool: True if upload successful, False otherwise
    """
    s3_client = get_s3_client()
    
    # Convert string to bytes if necessary
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    try:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=content)
        logger.info(f"File '{key}' uploaded to bucket '{bucket_name}'")
        return True
    
    except ClientError as e:
        logger.error(f"Error uploading file '{key}' to bucket '{bucket_name}': {e}")
        return False

def read_file(bucket_name, key):
    """
    Read content from an S3 object.
    
    Args:
        bucket_name (str): Source bucket name
        key (str): Object key (path)
    
    Returns:
        str: Object content (UTF-8 decoded) or None if error
    """
    s3_client = get_s3_client()
    
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        return content
    
    except ClientError as e:
        logger.error(f"Error reading file '{key}' from bucket '{bucket_name}': {e}")
        raise Exception(f"File read error: {e}")

def update_file(bucket_name, key, content):
    """
    Update an S3 object (same as upload_file, S3 overwrites by default).
    
    Args:
        bucket_name (str): Target bucket name
        key (str): Object key (path)
        content (str or bytes): New content
    
    Returns:
        bool: True if update successful, False otherwise
    """
    return upload_file(bucket_name, key, content)

def delete_file(bucket_name, key):
    """
    Delete an S3 object.
    
    Args:
        bucket_name (str): Bucket name
        key (str): Object key (path)
    
    Returns:
        bool: True if deletion successful, False otherwise
    """
    s3_client = get_s3_client()
    
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=key)
        logger.info(f"File '{key}' deleted from bucket '{bucket_name}'")
        return True
    
    except ClientError as e:
        logger.error(f"Error deleting file '{key}' from bucket '{bucket_name}': {e}")
        return False

def list_files(bucket_name, prefix=''):
    """
    List all files in a bucket, optionally filtered by prefix.
    
    Args:
        bucket_name (str): Bucket name
        prefix (str, optional): Key prefix to filter by
    
    Returns:
        list: List of object keys
    """
    s3_client = get_s3_client()
    
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    
    except ClientError as e:
        logger.error(f"Error listing objects in bucket '{bucket_name}': {e}")
        return []

def delete_bucket(bucket_name, force=False):
    """
    Delete an S3 bucket. If force=True, delete all objects first.
    
    Args:
        bucket_name (str): Bucket to delete
        force (bool): If True, delete all objects in the bucket first
    
    Returns:
        bool: True if deletion successful, False otherwise
    """
    s3_client = get_s3_client()
    
    try:
        if force:
            # Delete all objects in the bucket first
            objects = list_files(bucket_name)
            if objects:
                for key in objects:
                    delete_file(bucket_name, key)
        
        s3_client.delete_bucket(Bucket=bucket_name)
        logger.info(f"Bucket '{bucket_name}' deleted")
        return True
    
    except ClientError as e:
        logger.error(f"Error deleting bucket '{bucket_name}': {e}")
        return False

def get_s3_client(endpoint_url=None):
    return boto3.client(
        's3',
        aws_access_key_id="test",
        aws_secret_access_key="test",
        endpoint_url=endpoint_url,
        region_name="us-east-1"
    )

def upload_large_file(file_path, bucket_name, object_name, endpoint_url=None):
    s3_client = get_s3_client(endpoint_url)
    config = boto3.s3.transfer.TransferConfig(
        multipart_threshold=5 * 1024 * 1024,  # 5MB
        multipart_chunksize=5 * 1024 * 1024   # 5MB
    )

    try:
        s3_client.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=object_name,
            Config=config
        )
        print(f"Upload successful: {object_name}")
    except Exception as e:
        print(f"Upload failed: {e}")

def create_bucket(bucket_name, endpoint_url=None):
    s3_client = get_s3_client(endpoint_url)
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created successfully.")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket {bucket_name} already exists.")
    except Exception as e:
        print(f"Bucket creation failed: {e}")