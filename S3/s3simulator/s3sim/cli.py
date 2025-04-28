"""
Command Line Interface for S3Sim.
"""
import argparse
import os
import sys
import json
from s3sim.s3_operations import (
    create_bucket,
    delete_bucket,
    list_buckets,
    upload_file,
    read_file,
    delete_file,
    list_files,
    load_config_from_file
)

def main():
    """Run the S3Sim CLI."""
    parser = argparse.ArgumentParser(description='S3Sim - AWS S3 Simulator CLI')
    
    # Global options
    parser.add_argument('--endpoint', help='S3 endpoint URL (overrides environment variable)')
    parser.add_argument('--profile', help='AWS profile name for authentication')
    parser.add_argument('--config', help='Path to config file', default='s3sim_config.json')
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest='command', help='S3 operations')
    
    # create-bucket command
    create_bucket_parser = subparsers.add_parser('create-bucket', help='Create an S3 bucket')
    create_bucket_parser.add_argument('bucket_name', help='Name of the bucket to create')
    create_bucket_parser.add_argument('--region', help='AWS region for the bucket')
    
    # list-buckets command
    subparsers.add_parser('list-buckets', help='List all S3 buckets')
    
    # delete-bucket command
    delete_bucket_parser = subparsers.add_parser('delete-bucket', help='Delete an S3 bucket')
    delete_bucket_parser.add_argument('bucket_name', help='Name of the bucket to delete')
    delete_bucket_parser.add_argument('--force', action='store_true', 
                                     help='Force deletion by removing all objects first')
    
    # upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a file to S3')
    upload_parser.add_argument('bucket_name', help='Target bucket name')
    upload_parser.add_argument('key', help='Object key (path) in bucket')
    upload_parser.add_argument('content', help='Content to upload (or file path if --file is specified)')
    upload_parser.add_argument('--file', action='store_true', 
                              help='Treat content argument as a file path')
    upload_parser.add_argument('--metadata', help='Metadata as JSON string')
    
    # upload-large command
    upload_large_parser = subparsers.add_parser('upload-large', help='Upload a large file using multipart')
    upload_large_parser.add_argument('bucket_name', help='Target bucket name')
    upload_large_parser.add_argument('key', help='Object key (path) in bucket')
    upload_large_parser.add_argument('file_path', help='Path to the file to upload')
    upload_large_parser.add_argument('--part-size', type=int, default=5*1024*1024,
                                    help='Size of each part in bytes (default: 5MB)')
    upload_large_parser.add_argument('--metadata', help='Metadata as JSON string')
    
    # read command
    read_parser = subparsers.add_parser('read', help='Read a file from S3')
    read_parser.add_argument('bucket_name', help='Source bucket name')
    read_parser.add_argument('key', help='Object key (path) in bucket')
    
    # delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a file from S3')
    delete_parser.add_argument('bucket_name', help='Bucket name')
    delete_parser.add_argument('key', help='Object key (path) in bucket')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List files in a bucket')
    list_parser.add_argument('bucket_name', help='Bucket name')
    list_parser.add_argument('--prefix', default='', help='Key prefix to filter by')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command provided, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Load config file if specified
    if args.config:
        load_config_from_file(args.config)
    
    # Override endpoint URL if provided
    if args.endpoint:
        os.environ['S3_ENDPOINT_URL'] = args.endpoint
    
    # Execute requested command
    try:
        if args.command == 'create-bucket':
            success = create_bucket(args.bucket_name, args.region)
            if success:
                print(f"Bucket '{args.bucket_name}' created successfully")
            else:
                print(f"Failed to create bucket '{args.bucket_name}'")
                sys.exit(1)
                
        elif args.command == 'list-buckets':
            buckets = list_buckets()
            if buckets:
                print("Buckets:")
                for bucket in buckets:
                    print(f"  {bucket}")
            else:
                print("No buckets found")
                
        elif args.command == 'delete-bucket':
            success = delete_bucket(args.bucket_name, args.force)
            if success:
                print(f"Bucket '{args.bucket_name}' deleted successfully")
            else:
                print(f"Failed to delete bucket '{args.bucket_name}'")
                sys.exit(1)
                
        elif args.command == 'upload':
            # Handle content from file or command line
            content = args.content
            if args.file:
                with open(args.content, 'r') as f:
                    content = f.read()
            
            # Process metadata if provided
            metadata = None
            if args.metadata:
                try:
                    metadata = json.loads(args.metadata)
                except json.JSONDecodeError:
                    print("Error: metadata must be valid JSON")
                    sys.exit(1)
            
            success = upload_file(args.bucket_name, args.key, content, metadata=metadata)
            if success:
                print(f"File '{args.key}' uploaded to bucket '{args.bucket_name}' successfully")
            else:
                print(f"Failed to upload file '{args.key}' to bucket '{args.bucket_name}'")
                sys.exit(1)
                
        elif args.command == 'upload-large':
            # Process metadata if provided
            metadata = None
            if args.metadata:
                try:
                    metadata = json.loads(args.metadata)
                except json.JSONDecodeError:
                    print("Error: metadata must be valid JSON")
                    sys.exit(1)
            
            from s3sim.s3_operations import upload_large_file
            success = upload_large_file(
                args.bucket_name, 
                args.key, 
                args.file_path, 
                part_size=args.part_size,
                metadata=metadata
            )
            if success:
                print(f"Large file '{args.key}' uploaded to bucket '{args.bucket_name}' successfully")
            else:
                print(f"Failed to upload large file '{args.key}' to bucket '{args.bucket_name}'")
                sys.exit(1)
                
        elif args.command == 'read':
            try:
                content = read_file(args.bucket_name, args.key)
                print(content)
            except Exception as e:
                print(f"Error reading file: {e}")
                sys.exit(1)
                
        elif args.command == 'delete':
            success = delete_file(args.bucket_name, args.key)
            if success:
                print(f"File '{args.key}' deleted from bucket '{args.bucket_name}' successfully")
            else:
                print(f"Failed to delete file '{args.key}' from bucket '{args.bucket_name}'")
                sys.exit(1)
                
        elif args.command == 'list':
            files = list_files(args.bucket_name, args.prefix)
            if files:
                print(f"Objects in bucket '{args.bucket_name}':")
                for file in files:
                    print(f"  {file}")
            else:
                print(f"No objects found in bucket '{args.bucket_name}'")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()