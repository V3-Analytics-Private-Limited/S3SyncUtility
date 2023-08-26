import sys
import os
import boto3

from botocore.exceptions import BotoCoreError, NoCredentialsError
from s3sync.commands.state_management import load_state, save_state
from s3sync.commands.size import get_total_download_size, format_size
from s3sync.commands.common import get_total_download_objects

def download_from_s3(s3_bucket, s3_prefix, directory, exclude_list, dry_run=False, verbose=False):
    # Load the state from the .state.json file
    state = load_state()

    # Initialize the S3 client
    s3 = boto3.client('s3')

    try:
        print("Downloading from S3:")
        print(f"Bucket: {s3_bucket}")
        print(f"Downloading From: {s3_prefix}")

        # Calculate total objects and download size
        total_objects = get_total_download_objects(s3_bucket, s3_prefix)
        download_size = get_total_download_size(s3_bucket, s3_prefix, exclude_list)
        print(f"Total Objects: {total_objects}")
        print(f"Total download size: {format_size(download_size)}")

        # Confirm the download
        confirm = input("Proceed with download? (yes/no): ").lower()
        if confirm == 'yes':
            try:
                response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
                for obj in response.get('Contents', []):
                    s3_key = obj['Key']
                    if not any(item in s3_key for item in exclude_list):
                        local_path = os.path.join(directory, os.path.relpath(s3_key, s3_prefix))

                        # Initialize remote_etag
                        remote_etag = None

                        if os.path.exists(local_path):
                            # Get the remote ETag (checksum)
                            remote_etag = obj.get('ETag', '').strip('"')

                            # Get the local checksum from state
                            local_checksum = state.get(local_path, '')

                            # Compare local checksum with remote ETag
                            if local_checksum == remote_etag:
                                if verbose:
                                    print(f"Skipping {s3_key} as it's already downloaded and unchanged.")
                                continue

                        # Download the file
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
                            # Update state with new checksum
                            state[local_path] = remote_etag
                # Save updated state
                save_state(state)
            except (BotoCoreError, NoCredentialsError) as e:
                print(f"Error occurred: {e}")
        else:
            print("Download operation canceled.")

    except KeyboardInterrupt:
        print("\nOperation interrupted by the user.")
        sys.exit(0)