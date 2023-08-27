import sys
import os
import time
import boto3

from botocore.exceptions import BotoCoreError, NoCredentialsError
from s3sync_util.commands.state_management import load_state, save_state
from s3sync_util.commands.size import get_total_download_size, format_size
from s3sync_util.commands.common import get_total_download_objects, format_time


def download_from_s3(s3_bucket:str, s3_prefix:str, directory:str, exclude_list:list, dry_run:bool=False, progress:bool=False, verbose:bool=False) -> None:
    """Download files(s) from an S3 bucket to a local directory.
    Args:
        s3_bucket (str): The name of the S3 bucket.
        s3_prefix (str): The prefix to filter S3 objects.
        local_dir (str): The local directory to save downloaded file(s).
        exclude_list (list): List of items to exclude from download.
        dry_run (bool, optional): Simulate the download process without actual download. Defaults to False.
        progress (bool, optional): Display progress statistics. Defaults to False.
        verbose (bool, optional): Increase verbosity of the download process. Defaults to False.
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

        total_objects = get_total_download_objects(s3_bucket, s3_prefix)
        download_size = get_total_download_size(s3_bucket, s3_prefix, exclude_list)
        print(f"Total Objects: {total_objects}")
        print(f"Total download size: {format_size(download_size)}")

        confirm = input("Proceed with download? (yes/no): ").lower()
        if confirm == 'yes':
            state = load_state()

            downloaded_files = 0
            total_files = total_objects
            skipped_files = 0
            start_time = time.time()

            try:
                s3 = boto3.client('s3')
                response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
                for obj in response.get('Contents', []):
                    s3_key = obj['Key']
                    if not any(item in s3_key for item in exclude_list):
                        local_path = os.path.join(directory, os.path.relpath(s3_key, s3_prefix))
                        remote_etag = obj.get('ETag', '').strip('"')
                        last_modified = obj.get('LastModified', None)
                        if os.path.exists(local_path):
                            # local_checksum = state.get(local_path, {}).get('hash', '')
                            if remote_etag in state:
                                if verbose:
                                    print(f"Skipping {s3_key} as it's already downloaded and unchanged.")
                                skipped_files += 1
                                continue
                        # Download the file(s)
                        downloaded_files += 1
                        if progress:
                            if downloaded_files > skipped_files:
                                progress_percentage = (downloaded_files / (total_files - skipped_files)) * 100
                                remaining_files = total_files - downloaded_files
                                time_elapsed = time.time() - start_time
                                files_per_second = downloaded_files / time_elapsed
                                time_remaining = remaining_files / files_per_second
                                progress_line = f"Progress: {progress_percentage:.2f}% | Downloaded: {downloaded_files}/{total_files} | Remaining: {format_time(time_remaining)}"
                            else:
                                progress_percentage = 0
                                time_remaining = -1
                                progress_line = f"Progress: {progress_percentage:.2f}% | Downloaded: {downloaded_files}/{total_files} | Remaining: N/A"
                                sys.stdout.write("\r" + progress_line)
                                sys.stdout.flush()
                        if dry_run:
                            print(f"\nSimulating: Would download {s3_key} from S3 bucket {s3_bucket} to {local_path}")
                        else:
                            # print(f"Downloading {s3_key} from S3 bucket {s3_bucket}")
                            if verbose:
                                print(f"S3 Key: {s3_key}")
                                print(f"Local Path: {local_path}")
                            os.makedirs(os.path.dirname(local_path), exist_ok=True)
                            s3.download_file(s3_bucket, s3_key, local_path)
                            if verbose:
                                print(f"\nDownloaded {s3_key} as {local_path}")
                            state[local_path] = {'hash': remote_etag, 'last_modified': last_modified.isoformat(), 'extension': os.path.splitext(s3_key)[-1]}
                save_state(state)
                print("\nDownload completed.")
            except (BotoCoreError, NoCredentialsError) as e:
                print(f"Error occurred: {e}")
        else:
            print("Download operation canceled.")

    except KeyboardInterrupt:
        print("\nOperation interrupted by the user.")
        sys.exit(0)
