# S3 Operations Library

A Python library that provides a unified interface to interact with AWS S3 storage, with support for local testing using Moto.

## What is Boto3 and Moto?

- **Boto3** is the Amazon Web Services (AWS) SDK for Python. It allows Python developers to write software that makes use of AWS services like S3 (Simple Storage Service).

- **Moto** is a library that allows you to easily mock AWS services in your Python tests. This means you can test your code that interacts with AWS without actually connecting to AWS and incurring costs or requiring internet connectivity.

## Features

- Create and manage S3 buckets
- Upload and download files to/from S3
- Read file content directly from S3
- Delete files from S3
- Local storage mirroring for testing and development
- Seamless switching between real AWS S3 and Moto mock

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/s3-operations-lib.git
cd s3-operations-lib
```

### Step 2: Create the file structure

Create the following file structure:

```
s3_operations_lib/
├── __init__.py
├── __main__.py
├── config.py
├── s3_operations.py
├── cli.py
tests/
├── test_s3_operations.py
├── finaltest.py
setup.py
```

### Step 3: Copy the code files

Copy the code from each file provided into the respective files in your local folder structure.

#### `s3_operations_lib/__init__.py`

```python
# __init__.py

from .config import Config
from .s3_operations import S3Operations

__all__ = ["Config", "S3Operations"]
```

#### `s3_operations_lib/__main__.py`

```python
import click
from s3_operations_lib.s3_operations import S3Operations

@click.group()
def cli():
    pass

@cli.command()
@click.argument("bucket_name")
def create_bucket(bucket_name):
    s3_ops = S3Operations()
    s3_ops.start()
    s3_ops.create_bucket(bucket_name)
    s3_ops.stop()
    click.echo(f"Bucket '{bucket_name}' created.")

@cli.command()
def list_buckets():
    s3_ops = S3Operations()
    s3_ops.start()
    buckets = s3_ops.list_buckets()
    s3_ops.stop()
    for b in buckets:
        click.echo(b["Name"])

if __name__ == "__main__":
    cli()
```

#### `s3_operations_lib/config.py`

```python
import os
import boto3
from moto import mock_aws

class Config:
    def __init__(self, mode='moto'):
        self.mode = mode
        self.local_storage_path = os.path.join(os.getcwd(), "local_storage", "moto")
        self.aws_local_storage_path = os.path.join(os.getcwd(), "local_storage", "aws")
        self.endpoint_url = 'http://localhost:5000' if mode == 'moto' else None
        self.aws_access_key_id = 'test' if mode == 'moto' else os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = 'test' if mode == 'moto' else os.getenv('AWS_SECRET_ACCESS_KEY')
        self.use_moto = (mode == 'moto')

        if self.use_moto:
            self.s3_client = mock_aws()
        else:
            self.s3_client = boto3.client('s3',
                                        aws_access_key_id=self.aws_access_key_id,
                                        aws_secret_access_key=self.aws_secret_access_key)

    def get_local_storage_path(self):
        return self.local_storage_path if self.use_moto else self.aws_local_storage_path
```

#### `s3_operations_lib/s3_operations.py`

```python
import os
import shutil
import boto3
from botocore.exceptions import ClientError

class S3Operations:
    def __init__(self, config):
        self.config = config
        self.local_path = config.get_local_storage_path() # Assuming config has this method
        self.mock = None

        if config.use_moto:
            # Start the mock and create a proper client
            # Assuming config.s3_client is the moto mock starter/decorator
            self.mock = config.s3_client # This might need adjustment depending on how moto is integrated
            # If moto is used as a decorator, the client might be passed directly
            # If it's a separate starter, you might need to start it here
            print("Using Moto mock")
            # self.mock.start() # Only if config.s3_client is a mock starter instance

            # Create the boto3 client pointed to the moto server
            # Ensure config has endpoint_url, aws_access_key_id, aws_secret_access_key
            self.client = boto3.client(
                's3',
                endpoint_url=config.endpoint_url,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key,
                region_name='us-east-1' # Or a region from config if available
            )
        else:
            # Use the actual boto3 client provided by the config
            print("Using real S3 client")
            self.client = config.s3_client # Assuming config provides a configured boto3 client

    def _ensure_local_dir(self, path):
        """Ensures a local directory exists."""
        try:
            os.makedirs(path, exist_ok=True)
            # print(f"Ensured local directory exists: {path}") # Optional: add for verbose logging
        except OSError as e:
            print(f"Error creating local directory {path}: {e}")
            raise

    def create_bucket(self, bucket_name):
        """Creates an S3 bucket."""
        try:
            self.client.create_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        except ClientError as e:
            if e.response['Error']['Code'] in ['BucketAlreadyOwnedByYou', 'BucketAlreadyExists']:
                print(f"Bucket '{bucket_name}' already exists.")
            else:
                print(f"Error creating bucket '{bucket_name}': {e}")
                raise
        except Exception as e:
             print(f"An unexpected error occurred creating bucket '{bucket_name}': {e}")
             raise


    def upload_file(self, bucket_name, object_name, file_path):
        """Uploads a file to S3 and mirrors it locally."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Source file not found: {file_path}")

            self.client.upload_file(file_path, bucket_name, object_name)
            print(f"Uploaded '{object_name}' to bucket '{bucket_name}'.")

            # Mirror to local storage
            local_dir = os.path.join(self.local_path, bucket_name)
            self._ensure_local_dir(local_dir)
            local_file_path = os.path.join(local_dir, object_name)
            shutil.copy2(file_path, local_file_path)
            print(f"Mirrored '{object_name}' to local storage: {local_file_path}")

        except Exception as e:
            print(f"Error uploading file: {e}")
            raise

    def download_file(self, bucket_name, object_name, download_path):
        """Downloads a file from S3 and mirrors it locally."""
        try:
            # Ensure the local download directory exists
            download_dir = os.path.dirname(download_path)
            self._ensure_local_dir(download_dir)

            self.client.download_file(bucket_name, object_name, download_path)
            print(f"Downloaded '{object_name}' from bucket '{bucket_name}' to '{download_path}'.")

            # Mirror to local storage
            local_dir = os.path.join(self.local_path, bucket_name)
            self._ensure_local_dir(local_dir)
            local_file_path = os.path.join(local_dir, object_name)
            shutil.copy2(download_path, local_file_path)
            print(f"Mirrored '{object_name}' to local storage: {local_file_path}")

        except ClientError as e:
             if e.response['Error']['Code'] == '404':
                 print(f"Object '{object_name}' not found in bucket '{bucket_name}'.")
             else:
                 print(f"ClientError downloading file: {e}")
             raise
        except Exception as e:
            print(f"Error downloading file: {e}")
            raise

    def read_file(self, bucket_name, object_name):
        """Reads the content of an S3 object."""
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=object_name)
            content = response["Body"].read().decode("utf-8")
            print(f"Retrieved content from '{object_name}' in bucket '{bucket_name}'")
            return content
        except ClientError as e:
             if e.response['Error']['Code'] == 'NoSuchKey':
                 print(f"Object '{object_name}' not found in bucket '{bucket_name}'.")
             else:
                 print(f"ClientError reading file: {e}")
             raise
        except Exception as e:
            print(f"Error reading file: {e}")
            raise

    def delete_file(self, bucket_name, object_name):
        """Deletes a file from S3 and its local mirror."""
        try:
            self.client.delete_object(Bucket=bucket_name, Key=object_name)
            print(f"Deleted '{object_name}' from bucket '{bucket_name}'.")

            # Delete local mirrors
            # Assuming config might have multiple local storage paths or just one
            local_mirror_paths_to_check = [self.local_path]
            # If config.aws_local_storage_path is different and relevant, add it
            if hasattr(self.config, 'aws_local_storage_path') and self.config.aws_local_storage_path != self.local_path:
                 local_mirror_paths_to_check.append(self.config.aws_local_storage_path)


            for base_path in local_mirror_paths_to_check:
                file_path = os.path.join(base_path, bucket_name, object_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted local mirror: {file_path}")
                else:
                    print(f"Local mirror not found (already deleted or not present): {file_path}")

        except ClientError as e:
            # Handle cases where the object might not exist on S3
             if e.response['Error']['Code'] == 'NoSuchKey':
                 print(f"Object '{object_name}' not found in bucket '{bucket_name}' (already deleted).")
             else:
                 print(f"ClientError deleting file: {e}")
             raise
        except Exception as e:
            print(f"Error deleting file: {e}")
            raise

    def cleanup(self, bucket_name=None, remove_local=True, remove_bucket=False):
        """
        Clean up resources based on user preferences.

        Args:
            bucket_name: Name of bucket to clean (optional).
            remove_local: Whether to remove local files (default True).
            remove_bucket: Whether to remove the bucket (default False).
                         Bucket removal is only attempted if using moto mock.
        """
        print("\nInitiating cleanup...")
        try:
            if remove_local:
                print("Attempting to remove local storage...")
                local_storage_paths_to_clean = [self.local_path]
                # If config.aws_local_storage_path is different and relevant, add it
                if hasattr(self.config, 'aws_local_storage_path') and self.config.aws_local_storage_path != self.local_path:
                    local_storage_paths_to_clean.append(self.config.aws_local_storage_path)

                for path in local_storage_paths_to_clean:
                    if os.path.exists(path):
                        print(f"Removing local directory: {path}")
                        shutil.rmtree(path)
                        print(f"Cleaned up local storage: {path}")
                    else:
                        print(f"Local storage path not found (no cleanup needed): {path}")


            # Bucket removal is generally only safe and intended during testing with moto
            if remove_bucket and bucket_name and self.config.use_moto:
                print(f"Attempting to remove bucket '{bucket_name}' (using moto mock)...")
                try:
                    # List and delete all objects in the bucket first
                    print(f"Listing objects in bucket '{bucket_name}'...")
                    # Use paginator for potentially large number of objects
                    paginator = self.client.get_paginator('list_objects_v2')
                    pages = paginator.paginate(Bucket=bucket_name)

                    delete_objects = []
                    for page in pages:
                        if 'Contents' in page:
                            for obj in page['Contents']:
                                delete_objects.append({'Key': obj['Key']})

                    if delete_objects:
                        print(f"Deleting {len(delete_objects)} objects from bucket: {bucket_name}")
                        # S3 Batch delete supports up to 1000 objects per request
                        for i in range(0, len(delete_objects), 1000):
                             batch = delete_objects[i:i+1000]
                             self.client.delete_objects(
                                 Bucket=bucket_name,
                                 Delete={'Objects': batch}
                             )
                        print(f"Deleted all objects from bucket: {bucket_name}")
                    else:
                        print(f"No objects found in bucket '{bucket_name}'.")

                    # Then delete the bucket itself
                    print(f"Deleting bucket: {bucket_name}")
                    self.client.delete_bucket(Bucket=bucket_name)
                    print(f"Deleted bucket: {bucket_name}")

                except ClientError as e:
                     if e.response['Error']['Code'] == 'NoSuchBucket':
                         print(f"Bucket '{bucket_name}' not found (already deleted).")
                     elif e.response['Error']['Code'] == 'BucketNotEmpty':
                         print(f"Bucket '{bucket_name}' is not empty. Could not delete.")
                         # This case should ideally not happen if object deletion worked, but good to handle
                     else:
                         print(f"ClientError deleting bucket '{bucket_name}': {e}")
                         raise # Re-raise other ClientErrors
                except Exception as e:
                     print(f"An unexpected error occurred during bucket deletion: {e}")
                     raise
            elif remove_bucket and bucket_name and not self.config.use_moto:
                 print("Warning: Bucket removal is set to True but not using moto mock. Skipping real bucket deletion.")


        except Exception as e:
            print(f"An error occurred during cleanup: {e}")
            # Consider whether to re-raise or just log/print
            # raise

    def stop_mock(self):
        """Stops the moto mock server if it was started."""
        if self.mock and hasattr(self.mock, 'stop'):
            print("Attempting to stop Moto mock...")
            try:
                self.mock.stop()
                print("Moto mock stopped.")
            except Exception as e:
                print(f"Error stopping moto mock: {e}")
        elif self.mock:
             print("Mock object does not have a stop method. Skipping stop.")
        else:
            print("No mock instance to stop.")
```

#### `s3_operations_lib/cli.py`

```python
import click
from s3_operations_lib.config import Config
from s3_operations_lib.s3_operations import S3Operations
import os
import botocore.exceptions
import boto3

def auto_detect_mode():
    try:
        boto3.client("sts").get_caller_identity()
        return "aws"
    except botocore.exceptions.NoCredentialsError:
        return "moto"
    except botocore.exceptions.ClientError:
        return "moto"

@click.group()
def cli():
    pass

@cli.command()
@click.argument('bucket')
def create_bucket(bucket):
    mode = auto_detect_mode()
    click.echo(f"Using mode: {mode}")
    config = Config(mode=mode)
    s3 = S3Operations(config)
    s3.create_bucket(bucket)
    click.echo(f"Bucket '{bucket}' created.")
    if mode == "moto":
        s3.stop_mock()

@cli.command()
@click.argument('bucket')
@click.argument('file_path')
@click.argument('object_name')
def upload_file(bucket, file_path, object_name):
    mode = auto_detect_mode()
    click.echo(f"Using mode: {mode}")
    config = Config(mode=mode)
    s3 = S3Operations(config)
    s3.upload_file(bucket, file_path, object_name)
    click.echo(f"Uploaded {file_path} to {bucket}/{object_name}")
    if mode == "moto":
        s3.stop_mock()

@cli.command()
@click.argument('bucket')
@click.argument('object_name')
@click.argument('download_path')
def download_file(bucket, object_name, download_path):
    mode = auto_detect_mode()
    click.echo(f"Using mode: {mode}")
    config = Config(mode=mode)
    s3 = S3Operations(config)
    s3.download_file(bucket, object_name, download_path)
    click.echo(f"Downloaded {object_name} from {bucket} to {download_path}")
    if mode == "moto":
        s3.stop_mock()

@cli.command()
@click.argument('bucket')
@click.argument('object_name')
def read_file(bucket, object_name):
    mode = auto_detect_mode()
    click.echo(f"Using mode: {mode}")
    config = Config(mode=mode)
    s3 = S3Operations(config)
    content = s3.read_file(bucket, object_name)
    click.echo(f"File content: {content}")
    if mode == "moto":
        s3.stop_mock()

if __name__ == '__main__':
    cli()
```

#### `tests/test_s3_operations.py`

```python
import os
import pytest
from s3_operations_lib.s3_operations import S3Operations
from s3_operations_lib.config import Config

@pytest.fixture
def s3_ops():
    config = Config(mode='moto')
    s3 = S3Operations(config)
    yield s3
    s3.stop_mock()

def test_create_and_list_bucket(s3_ops):
    s3_ops.create_bucket("test-bucket")
    # Add assertions here
```

#### `tests/finaltest.py`

```python
from s3_operations_lib.config import Config
from s3_operations_lib.s3_operations import S3Operations
import os

def run_test():
    print("----- MOTO MODE TEST -----")
    config = Config(mode='moto')
    s3 = S3Operations(config)

    bucket_name = "test-bucket"
    file_name = "sample.txt"
    file_content = "This is a test file content from Moto mode."
    
    try:
        # Ensure local storage directory exists
        os.makedirs(config.local_storage_path, exist_ok=True)
        local_path = os.path.join(config.local_storage_path, file_name)

        # Write a sample file
        with open(local_path, 'w') as f:
            f.write(file_content)
        print(f"Created test file at: {local_path}")

        # Create bucket
        print("\nCreating bucket...")
        s3.create_bucket(bucket_name)

        # Upload file
        print("\nUploading file...")
        s3.upload_file(bucket_name, file_name, local_path)

        # Read file
        print("\nReading file content from S3...")
        content = s3.read_file(bucket_name, file_name)
        print(f"\nContent read from S3:\n{content}")

        # Download file
        print("\nDownloading file to verify...")
        download_path = os.path.join(config.local_storage_path, "downloaded_sample.txt")
        s3.download_file(bucket_name, file_name, download_path)

        # Verify download
        if os.path.exists(download_path):
            with open(download_path, 'r') as f:
                downloaded = f.read()
                print(f"\nDownloaded Content:\n'{downloaded}'")
                
                assert downloaded.strip() == file_content.strip(), \
                    f"Content mismatch! Expected: '{file_content.strip()}', Got: '{downloaded.strip()}'"
                print("\nContent verification successful!")

        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        raise
    finally:
        # Ask user if they want to cleanup
        cleanup = input("\nDo you want to cleanup resources? (y/n): ").strip().lower()
        if cleanup == 'y':
            print("\nCleaning up resources...")
            s3.delete_file(bucket_name, file_name)
            s3.cleanup(bucket_name)
            print("Cleanup complete.")
        else:
            print("\nSkipping cleanup. Resources remain available.")
        
        s3.stop_mock()

if __name__ == "__main__":
    run_test()
```

#### `setup.py`

```python
from setuptools import setup, find_packages

setup(
    name='s3_operations_lib',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'moto==5.1.4',
        'click'
    ],
    entry_points={
        'console_scripts': [
            's3cli = s3_operations_lib.cli:cli',
        ],
    },
    author='Your Name',
    description='Unified interface between AWS S3 and Moto',
    python_requires='>=3.7',
)
```

### Step 4: Install the required packages

Run the following command to install the required packages:

```bash
pip install boto3 moto==5.1.4 click pytest
```

### Step 5: Install the package in development mode

From the root directory of the project, run:

```bash
pip install -e .
```

This will install the package in development mode, which means you can modify the code and see the changes without reinstalling.

## Usage

### Using the CLI

After installation, you can use the command line interface to interact with S3:

```bash
# Create a bucket
s3cli create-bucket my-bucket

# Upload a file
s3cli upload-file my-bucket /path/to/local/file.txt my-object-name

# Download a file
s3cli download-file my-bucket my-object-name /path/to/save/downloaded/file.txt

# Read a file
s3cli read-file my-bucket my-object-name
```

### Using the Library in Python code

```python
from s3_operations_lib.config import Config
from s3_operations_lib.s3_operations import S3Operations

# Create a configuration
config = Config(mode='moto')  # Use 'moto' for testing, 'aws' for real AWS

# Create an S3 Operations instance
s3 = S3Operations(config)

# Create a bucket
s3.create_bucket('my-bucket')

# Upload a file
s3.upload_file('my-bucket', 'my-object-name', '/path/to/local/file.txt')

# Read a file
content = s3.read_file('my-bucket', 'my-object-name')
print(content)

# Download a file
s3.download_file('my-bucket', 'my-object-name', '/path/to/save/downloaded/file.txt')

# Delete a file
s3.delete_file('my-bucket', 'my-object-name')

# Clean up resources
s3.cleanup(bucket_name='my-bucket', remove_local=True, remove_bucket=True)

# Stop the mock (only needed when using 'moto' mode)
s3.stop_mock()
```

## Testing

### Running the tests

To run the tests, use pytest:

```bash
pytest tests/test_s3_operations.py
```

### Running the final test

To run the final test that verifies all functionality:

```bash
python tests/finaltest.py
```

## Modes

The library supports two modes:

1. **moto**: Uses the Moto mock for local testing without requiring AWS credentials or internet connectivity.
2. **aws**: Uses the real AWS S3 service.

When using the CLI, the mode is automatically detected based on whether AWS credentials are available. When using the library directly, you can specify the mode when creating the Config object.

## AWS Credentials

When using the 'aws' mode, you need to set up AWS credentials. There are several ways to do this:

1. **Environment variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

2. **AWS credentials file**:
   Create a file at `~/.aws/credentials` with the following content:
   ```
   [default]
   aws_access_key_id = your_access_key
   aws_secret_access_key = your_secret_key
   ```

3. **AWS config file**:
   Create a file at `~/.aws/config` with the following content:
   ```
   [default]
   region = us-east-1
   ```

## Troubleshooting

### Common issues

1. **ImportError: No module named 'moto'**:
   - Make sure you have installed the required packages: `pip install moto==5.1.4`

2. **boto3.exceptions.NoCredentialsError**:
   - This happens when using 'aws' mode without AWS credentials. Either set up AWS credentials or use 'moto' mode.

3. **Permission denied errors**:
   - When using 'aws' mode, make sure your AWS credentials have the necessary permissions for S3 operations.

### Fixing path issues

If you encounter errors related to local paths, make sure to update the paths in `config.py` to match your system:

```python
# In config.py
self.local_storage_path = os.path.join(os.getcwd(), "local_storage", "moto")
self.aws_local_storage_path = os.path.join(os.getcwd(), "local_storage", "aws")
```

## Contributing

Please feel free to contribute.
saarth.nikam@tihiitb.org
