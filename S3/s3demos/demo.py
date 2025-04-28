"""
Demo script showing S3Sim in action.

Run this with the Moto server running:
1. Start moto server in another terminal: moto_server -p 5000
2. Set environment variable: $env:S3_ENDPOINT_URL = "http://localhost:5000" (PowerShell)
3. Run this script: python demo.py
"""

import os
import sys
from s3sim.s3_operations import (
    create_bucket, list_buckets, upload_file, read_file, 
    update_file, list_files, delete_file, delete_bucket
)

def main():
    """Run the S3Sim demo."""
    # Check if the endpoint URL is set
    endpoint = os.environ.get('S3_ENDPOINT_URL')
    if endpoint:
        print(f"Using S3 simulator at: {endpoint}")
    else:
        print("Warning: S3_ENDPOINT_URL not set - using real AWS S3!")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Create a test bucket
    bucket_name = 'demo-bucket'
    print(f"\nCreating bucket: {bucket_name}")
    create_bucket(bucket_name)
    
    # List buckets
    buckets = list_buckets()
    print(f"Available buckets: {buckets}")
    
    # Upload some files
    print("\nUploading files...")
    upload_file(bucket_name, 'hello.txt', 'Hello, S3!')
    upload_file(bucket_name, 'data.json', '{"name": "test", "value": 42}')
    upload_file(bucket_name, 'folder/nested.txt', 'Nested file content')
    
    # List files
    print("\nAll files in bucket:")
    files = list_files(bucket_name)
    for file in files:
        print(f" - {file}")
    
    # Read a file
    file_key = 'hello.txt'
    print(f"\nReading {file_key}:")
    content = read_file(bucket_name, file_key)
    print(f"Content: {content}")
    
    # Update a file
    print(f"\nUpdating {file_key}")
    update_file(bucket_name, file_key, 'Updated content!')
    content = read_file(bucket_name, file_key)
    print(f"New content: {content}")
    
    # List files in subfolder
    print("\nFiles in 'folder/':")
    folder_files = list_files(bucket_name, prefix='folder/')
    for file in folder_files:
        print(f" - {file}")
    
    # Delete a file
    print(f"\nDeleting {file_key}")
    delete_file(bucket_name, file_key)
    
    # List remaining files
    print("\nRemaining files:")
    remaining_files = list_files(bucket_name)
    for file in remaining_files:
        print(f" - {file}")
    
    # Clean up
    print(f"\nDeleting bucket {bucket_name} with force=True")
    delete_bucket(bucket_name, force=True)
    
    print("\nDemo completed successfully!")

if __name__ == '__main__':
    main()