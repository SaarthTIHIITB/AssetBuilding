from s3sim.s3_operations import (
    create_bucket,
    upload_large_file
)
import os

# Configuration
ENDPOINT_URL = "http://localhost:5000"  # Moto server endpoint
BUCKET_NAME = "test-bucket"
TEST_FILE_PATH = "large_test_file.bin"
OBJECT_NAME = "uploaded_large_file.bin"

# Step 1: Create a dummy large file if it doesn't exist
if not os.path.exists(TEST_FILE_PATH):
    print(f"Creating a large test file ({TEST_FILE_PATH})...")
    with open(TEST_FILE_PATH, "wb") as f:
        f.seek((10 * 1024 * 1024) - 1)  # 10 MB file
        f.write(b'\0')
    print("Large test file created.")

# Step 2: Create Bucket
create_bucket(BUCKET_NAME, endpoint_url=ENDPOINT_URL)

# Step 3: Upload Large File
upload_large_file(TEST_FILE_PATH, BUCKET_NAME, OBJECT_NAME, endpoint_url=ENDPOINT_URL)
