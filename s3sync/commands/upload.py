import sys
import os
import boto3

from botocore.exceptions import BotoCoreError, NoCredentialsError
from s3sync.commands.common import get_total_objects


def upload_to_s3(directory, s3_bucket, s3_prefix, exclude_list, dry_run=False):
    """Upload files from a directory to an S3 bucket.

    Args:
        directory (str): The directory containing files to upload.
        s3_bucket (str): The name of the S3 bucket.
        s3_prefix (str): The prefix to use for S3 object keys.
        exclude_list (list): List of items to exclude from upload.
        dry_run (bool, optional): Simulate the upload process without actual upload. Defaults to False.
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
        print("Uploading to S3:")
        print(f"Bucket: {s3_bucket}")
        print(f"Uploading To: {s3_prefix}")
        print(f"Total Objects: {get_total_objects(directory, exclude_list)}")

        confirm = input("Proceed with upload? (yes/no): ").lower()
        if confirm == 'yes':

            try:
                s3 = boto3.client('s3')
                for root, dirs, files in os.walk(directory):
                    dirs[:] = [d for d in dirs if d not in exclude_list]
                    for file in files:
                        if file not in exclude_list:
                            local_path = os.path.join(root, file)
                            relative_path = os.path.relpath(local_path, directory)
                            s3_key = os.path.join(s3_prefix, relative_path)

                            if dry_run:
                                print(f"Simulating: Would upload {file} to S3 bucket {s3_bucket} as {s3_key}")
                            else:
                                print(f"Uploading {file} to S3 bucket {s3_bucket}")
                                s3.upload_file(local_path, s3_bucket, s3_key)
            except (BotoCoreError, NoCredentialsError) as e:
                print(f"Error occurred: {e}")
        else:
            print("Upload operation canceled.")

    except KeyboardInterrupt:
        print("\nOperation interrupted by the user.")
        sys.exit(0)