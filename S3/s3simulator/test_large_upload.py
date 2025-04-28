# test_large_upload.py
import os
import tempfile
from s3sim.s3_operations import (
    create_bucket,
    upload_large_file,
    list_files,
    delete_bucket
)

# Set endpoint for Moto server
os.environ['S3_ENDPOINT_URL'] = 'http://localhost:5000'

# Create a temporary large file (~15 MB for testing)
temp_dir = tempfile.gettempdir()
large_file_path = os.path.join(temp_dir, 'large_test_file.txt')

# Write 15MB of data
with open(large_file_path, 'w') as f:
    f.write('A' * 15 * 1024 * 1024)  # 15MB

# Test bucket name
bucket_name = 'large-file-bucket'

try:
    # Create bucket
    create_bucket(bucket_name, user_id='large_test_user')

    # Upload the large file using multipart upload
    upload_large_file(bucket_name, 'uploaded_large_file.txt', large_file_path, user_id='large_test_user')

    # List files in the bucket
    files = list_files(bucket_name, user_id='large_test_user')
    print(f"Files in bucket '{bucket_name}': {files}")

finally:
    # Clean up: Delete bucket and temp file
    delete_bucket(bucket_name, force=True, user_id='large_test_user')
    if os.path.exists(large_file_path):
        os.remove(large_file_path)
