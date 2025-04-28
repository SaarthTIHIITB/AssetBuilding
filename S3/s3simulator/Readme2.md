# S3Sim: AWS S3 Simulator

This package provides an easy way to work with AWS S3, configurable to work with either real AWS S3 or the Moto S3 simulator via an endpoint URL.

## Features

- **S3 Simulation**: Use Moto to simulate AWS S3 locally without needing real AWS credentials
- **Endpoint Configuration**: Switch between Moto and real AWS easily via configuration
- **Authentication Support**: AWS profile-based authentication for real AWS usage
- **Permission Controls**: User-based permission management for buckets and objects
- **Metadata Support**: Store and retrieve object metadata
- **Multipart Upload**: Efficient large file uploads with part-based approach
- **Command-Line Interface**: Easy to use CLI for common operations
- **Configuration Files**: Support for JSON-based configuration

## Installation

```bash
# Install the package
pip install -e .

# For development, install with the development dependencies
pip install -e ".[dev]"
```

## Basic Usage

You can use the package in your Python code:

```python
from s3sim.s3_operations import create_bucket, upload_file, read_file

# Use with Moto server (first run 'moto_server -p 5000' in another terminal)
import os
os.environ['S3_ENDPOINT_URL'] = 'http://localhost:5000'

# Create a bucket
create_bucket('my-bucket')

# Upload a file
upload_file('my-bucket', 'hello.txt', 'Hello, World!')

# Read the file
content = read_file('my-bucket', 'hello.txt')
print(content)  # 'Hello, World!'
```

## Command Line Interface

The package also provides a command-line interface:

```bash
# Start Moto server first
moto_server -p 5000

# Use CLI with Moto
s3sim --endpoint http://localhost:5000 create-bucket my-cli-bucket
s3sim --endpoint http://localhost:5000 upload my-cli-bucket test.txt "Hello from CLI"
s3sim --endpoint http://localhost:5000 list my-cli-bucket
s3sim --endpoint http://localhost:5000 read my-cli-bucket test.txt
```

## Configuration File

You can use a configuration file (`s3sim_config.json`) to set your preferences:

```json
{
    "endpoint_url": "http://localhost:5000",
    "region": "us-east-1",
    "default_user_id": "test_user"
}
```

## Advanced Features

### Authentication with AWS Profiles

```python
from s3sim.s3_operations import get_s3_client

# Use a specific AWS profile
s3_client = get_s3_client(profile_name='my-profile')
```

### Permission Management

```python
from s3sim.s3_operations import upload_file, read_file, permission_manager

# Create bucket and file as user1
create_bucket('shared-bucket', user_id='user1')
upload_file('shared-bucket', 'shared.txt', 'Shared content', user_id='user1')

# Grant read permission to user2
permission_manager.add_object_permission('shared-bucket', 'shared.txt', 'user2', 'read')

# Now user2 can read the file
content = read_file('shared-bucket', 'shared.txt', user_id='user2')
```

### Metadata Support

```python
from s3sim.s3_operations import upload_file, get_object_metadata

# Upload with metadata
metadata = {'author': 'John Doe', 'version': '1.0'}
upload_file('my-bucket', 'doc.txt', 'Content', metadata=metadata)

# Get metadata
retrieved_metadata = get_object_metadata('my-bucket', 'doc.txt')
print(retrieved_metadata)  # {'author': 'John Doe', 'version': '1.0'}
```

### Multipart Upload for Large Files

```python
from s3sim.s3_operations import upload_large_file

# Upload a large file
upload_large_file(
    'my-bucket',
    'large-file.bin',
    '/path/to/large/file.bin',
    part_size=5*1024*1024  # 5MB parts
)
```

## Testing

Run the tests with:

```bash
python test_s3sim.py
```

## Development

### Directory Structure

```
s3sim/
├── __init__.py
├── s3_operations.py  # Core functionality
├── cli.py           # Command-line interface
└── ...
```

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://your-repo/s3sim.git
cd s3sim

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```