import sys
import os
import boto3

from botocore.exceptions import BotoCoreError, NoCredentialsError
from s3sync.commands.common import get_total_objects_s3


def download_from_s3(s3_bucket, s3_prefix, directory, exclude_list, dry_run=False):
    """Download files from an S3 bucket to a local directory.

    Args:
        s3_bucket (str): The name of the S3 bucket.
        s3_prefix (str): The prefix to filter S3 objects.
        local_dir (str): The local directory to save downloaded files.
        exclude_list (list): List of items to exclude from download.
        dry_run (bool, optional): Simulate the download process without actual download. Defaults to False.
    """

    if not s3_bucket or not s3_prefix:
        if not s3_bucket and not s3_prefix:
            print("Error: Both --s3-bucket [S3_BUCKET] and --s3-prefix [S3_PREFIX] are required.")
        elif not s3_bucket:
            print("Error: --s3-bucket [S3_BUCKET] is required.")
        else:
            print("Error: --s3-prefix [S3_PREFIX] is required.")
        sys.exit(1)

    try:
        print("Downloading from S3:")
        print(f"Bucket: {s3_bucket}")
        print(f"Downloading From: {s3_prefix}")
        print(f"Total Objects: {get_total_objects_s3(s3_bucket, s3_prefix)}")
        confirm = input("Proceed with download? (yes/no): ").lower()
        if confirm == 'yes':

            try:
                s3 = boto3.client('s3')
                response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
                for obj in response.get('Contents', []):
                    s3_key = obj['Key']
                    if not any(item in s3_key for item in exclude_list):
                        local_path = os.path.join(directory, os.path.relpath(s3_key, s3_prefix))
                        
                        if dry_run:
                            print(f"Simulating: Would download {s3_key} from S3 bucket {s3_bucket} to {local_path}")
                        else:
                            print(f"Downloading {s3_key} from S3 bucket {s3_bucket}")
                            os.makedirs(os.path.dirname(local_path), exist_ok=True)
                            s3.download_file(s3_bucket, s3_key, local_path)
            except (BotoCoreError, NoCredentialsError) as e:
                print(f"Error occurred: {e}")
        else:
            print("Download operation canceled.")

    except KeyboardInterrupt:
        print("\nOperation interrupted by the user.")
        sys.exit(0)