import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone



def list_objects(s3_client, bucket_name):
    """List all objects in an S3 bucket."""
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                yield obj
    except ClientError as e:
        print(f"Error listing objects in bucket {bucket_name}: {e}")

def download_object(s3_client, bucket_name, object_key, local_path):
    """Download an object from S3 to the local file system."""
    try:
        s3_client.download_file(bucket_name, object_key, local_path)
        print(f"Downloaded {object_key} to {local_path}")
    except ClientError as e:
        print(f"Error downloading {object_key}: {e}")

def sync_bucket_to_local(bucket_name, local_directory, region_name='us-east-1'):
    """Sync objects from an S3 bucket to a local directory."""
    s3_client = boto3.client('s3', region_name=region_name)

    # Ensure the local directory exists
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    # List objects in the S3 bucket
    for obj in list_objects(s3_client, bucket_name):
        object_key = obj['Key']
        source_last_modified = obj['LastModified']

        # Construct local file path
        local_file_path = os.path.join(local_directory, object_key)

        # Check if local file exists and compare last modified dates
        if not os.path.exists(local_file_path):
            print(f"Object {object_key} not found locally. Downloading...")
            download_object(s3_client, bucket_name, object_key, local_file_path)
        else:
            local_last_modified = datetime.fromtimestamp(os.path.getmtime(local_file_path), timezone.utc)
            if source_last_modified > local_last_modified:
                print(f"Object {object_key} is newer in S3. Downloading...")
                download_object(s3_client, bucket_name, object_key, local_file_path)

def main():
    bucket_name = 'aptive.data-staging.pest-identification'
    local_directory = '/Users/ike.simmons/s3/pest_id'
    region_name = 'us-east-1'  # Change to your desired region

    sync_bucket_to_local(bucket_name, local_directory, region_name)

if __name__ == "__main__":
    main()