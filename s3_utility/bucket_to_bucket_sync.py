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

def copy_object(s3_client_dest, source_bucket, dest_bucket, object_key, s3_client_src):
    """Copy an object from the source bucket to the destination bucket."""
    try:
        copy_source = {
            'Bucket': source_bucket,
            'Key': object_key
        }
        s3_client_dest.copy_object(
            CopySource=copy_source,
            Bucket=dest_bucket,
            Key=object_key
        )
        print(f"Copied {object_key} from {source_bucket} to {dest_bucket}")
    except ClientError as e:
        print(f"Error copying {object_key}: {e}")

def sync_staging_to_production(staging_bucket, production_bucket, staging_access_key, staging_secret_key, production_access_key, production_secret_key, region_name):
    """Sync objects from the staging bucket to the production bucket."""
    # S3 client for the staging bucket (source)
    s3_client_src = boto3.client(
        's3',
        aws_access_key_id=staging_access_key,
        aws_secret_access_key=staging_secret_key,
        region_name=region_name
    )

    # S3 client for the production bucket (destination)
    s3_client_dest = boto3.client(
        's3',
        aws_access_key_id=production_access_key,
        aws_secret_access_key=production_secret_key,
        region_name=region_name
    )

    # List objects in both buckets
    source_objects = {obj['Key']: obj for obj in list_objects(s3_client_src, staging_bucket)}
    dest_objects = {obj['Key']: obj for obj in list_objects(s3_client_dest, production_bucket)}

    # Iterate over source objects and copy if necessary
    for key, source_obj in source_objects.items():
        if key not in dest_objects:
            print(f"Object {key} not found in destination bucket. Copying...")
            copy_object(s3_client_dest, staging_bucket, production_bucket, key, s3_client_src)
        else:
            source_last_modified = source_obj['LastModified']
            dest_last_modified = dest_objects[key]['LastModified']
            if source_last_modified > dest_last_modified:
                print(f"Object {key} is newer in source bucket. Copying...")
                copy_object(s3_client_dest, staging_bucket, production_bucket, key, s3_client_src)

def main():
    staging_access_key = 'ASIAWVQ5FO6O4U57ZFFJ'
    staging_secret_key = '9XOhvuaVkko/hnfbyxl9SPm+K+KJ+ufpPxFmxD6O'
    production_access_key = 'ASIAYVPXHZVHS3A2OWPB'
    production_secret_key = 'AVS5Wzcwrcw5TQLNDbjxisEd/QskHTbU04oJ7CS9'
    region_name = 'us-east-1' 

    # Bucket names
    staging_bucket = 'aptive.data-staging.pest-identification/pest_details/'
    production_bucket = 'aptive-env-ds'
    prod_prefix = 

    # Sync staging to production
    sync_staging_to_production(
        staging_bucket,
        production_bucket,
        staging_access_key,
        staging_secret_key,
        production_access_key,
        production_secret_key, 
        region_name
    )

if __name__ == "__main__":
    main()
    