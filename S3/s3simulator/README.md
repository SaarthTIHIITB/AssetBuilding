# S3Sim - AWS S3 Simulator Library

S3Sim is a Python library that wraps AWS S3 operations with the ability to use either real AWS S3 or the Moto S3 simulator. This makes it ideal for development and testing environments where real AWS access is limited.

## Features

- Full CRUD operations (Create, Read, Update, Delete) for S3 buckets and objects
- Seamless switching between Moto simulator and real AWS S3
- Proper error handling and logging
- Extensive test coverage

## Installation

Install the package from the project directory:

```bash
# Basic installation
pip install -e .

# For development (includes Moto and testing dependencies)
pip install -e .[dev]
```

## Usage

### Using with Moto Server

1. First, start the Moto server:

```bash
# In a separate terminal/command prompt
moto_server -p 5000
```

2. Set the environment variable to use the Moto endpoint:

```bash
# PowerShell
$env:S3_ENDPOINT_URL = "http://localhost:5000"

# Bash/Linux
export S3_ENDPOINT_URL="http://localhost:5000"
```

3. Use the library functions:

```python
from s3sim.s3_operations import create_bucket, upload_file, read_file

# Create a bucket
create_bucket('my-test-bucket')

# Upload a file
upload_file('my-test-bucket', 'hello.txt', 'Hello, world!')

# Read the file
content = read_file('my-test-bucket', 'hello.txt')
print(content)  # Output: Hello, world!
```

### Using with Real AWS S3

1. Unset the environment variable (or don't set it):

```bash
# PowerShell
Remove-Item Env:S3_ENDPOINT_URL

# Bash/Linux
unset S3_ENDPOINT_URL
```

2. Configure AWS credentials using any standard method:
   - AWS credentials file (~/.aws/credentials)
   - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
   - IAM roles (when running on AWS)

3. Use the exact same functions - they now work with real AWS:

```python
from s3sim.s3_operations import create_bucket, upload_file, read_file

# Create a bucket (with region for real AWS)
create_bucket('my-real-bucket', region='us-west-2')

# Upload and read work the same way
upload_file('my-real-bucket', 'hello.txt', 'Hello from real AWS!')
content = read_file('my-real-bucket', 'hello.txt')
```

## API Reference

### Basic Operations

- `create_bucket(bucket_name, region=None)` - Create a bucket
- `bucket_exists(bucket_name)` - Check if a bucket exists
- `list_buckets()` - List all buckets
- `delete_bucket(bucket_name, force=False)` - Delete a bucket (force=True deletes contents first)

### File Operations

- `upload_file(bucket_name, key, content)` - Upload content to S3
- `read_file(bucket_name, key)` - Read content from S3
- `update_file(bucket_name, key, content)` - Update existing content (same as upload)
- `delete_file(bucket_name, key)` - Delete a file from S3
- `list_files(bucket_name, prefix='')` - List files in a bucket, optionally filtered by prefix

## Running Tests

```bash
# Make sure you've installed development dependencies
pip install -e .[dev]

# Run tests with pytest
pytest s3sim/tests/

# For more verbose output
pytest -v s3sim/tests/
```

## Development Notes

- Tests use Moto's `mock_s3` decorator to simulate S3 entirely in memory
- No real AWS credentials or network access are needed for tests
- The library reads S3 paths automatically without requiring manual file creation
- Switching between Moto and real S3 requires only changing (or unsetting) an environment variable

## License

This project is licensed under the MIT License - see the LICENSE file for details.