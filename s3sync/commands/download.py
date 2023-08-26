import sys
import os
import boto3

from botocore.exceptions import BotoCoreError, NoCredentialsError
from s3sync.commands.state_management import load_state, save_state
from s3sync.commands.size import get_total_download_size, format_size
from s3sync.commands.common import get_total_download_objects


def download_from_s3(s3_bucket, s3_prefix, directory, exclude_list, dry_run=False, verbose=False):
    """Download files(s) from an S3 bucket to a local directory.
    Args:
        s3_bucket (str): The name of the S3 bucket.
        s3_prefix (str): The prefix to filter S3 objects.
        local_dir (str): The local directory to save downloaded file(s).
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

        # Calculate total objects and download size
        total_objects = get_total_download_objects(s3_bucket, s3_prefix)
        download_size = get_total_download_size(s3_bucket, s3_prefix, exclude_list)
        print(f"Total Objects: {total_objects}")
        print(f"Total download size: {format_size(download_size)}")

        confirm = input("Proceed with download? (yes/no): ").lower()
        if confirm == 'yes':
            state = load_state()

            try:
                s3 = boto3.client('s3')
                response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
                for obj in response.get('Contents', []):
                    s3_key = obj['Key']
                    if not any(item in s3_key for item in exclude_list):
                        local_path = os.path.join(directory, os.path.relpath(s3_key, s3_prefix))
                        # Get the remote ETag (checksum) and last modified timestamp
                        remote_etag = obj.get('ETag', '').strip('"')
                        last_modified = obj.get('LastModified', None)
                        if os.path.exists(local_path):
                            # Get the local checksum
                            local_checksum = state.get(local_path, {}).get('hash', '')
                            # Compare local checksumwith remote ETag
                            if local_checksum == remote_etag:
                                if verbose:
                                    print(f"Skipping {s3_key} as it's already downloaded and unchanged.")
                                continue
                        # Download the file(s)
                        if dry_run:
                            print(f"Simulating: Would download {s3_key} from S3 bucket {s3_bucket} to {local_path}")
                        else:
                            print(f"Downloading {s3_key} from S3 bucket {s3_bucket}")
                            if verbose:
                                print(f"S3 Key: {s3_key}")
                                print(f"Local Path: {local_path}")
                            os.makedirs(os.path.dirname(local_path), exist_ok=True)
                            s3.download_file(s3_bucket, s3_key, local_path)
                            if verbose:
                                print(f"Downloaded {s3_key} as {local_path}")
                            # Update state with new checksum, extension, and last modified timestamp
                            state[local_path] = {'hash': remote_etag, 'last_modified': last_modified.isoformat(), 'extension': os.path.splitext(s3_key)[-1]}
                # Save updated state
                save_state(state)
            except (BotoCoreError, NoCredentialsError) as e:
                print(f"Error occurred: {e}")
        else:
            print("Download operation canceled.")

    except KeyboardInterrupt:
        print("\nOperation interrupted by the user.")
        sys.exit(0)