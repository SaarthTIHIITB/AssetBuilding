"""
S3Sim - AWS S3 operations with Moto simulator support.

This package provides a set of functions for S3 operations that work with both
real AWS S3 and the Moto S3 simulator.
"""

from s3sim.s3_operations import (
    get_s3_client,
    create_bucket,
    bucket_exists,
    list_buckets,
    upload_file,
    read_file,
    update_file,
    delete_file,
    list_files,
    delete_bucket,
)

__version__ = '0.1.0'