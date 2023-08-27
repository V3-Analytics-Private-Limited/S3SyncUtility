import sys
import os
import boto3
import time
from datetime import datetime

from botocore.exceptions import BotoCoreError, NoCredentialsError
from s3sync_util.commands.size import get_total_upload_size, format_size
from s3sync_util.commands.common import get_total_upload_objects, format_time
from s3sync_util.commands.state_management import load_state, save_state, calculate_checksum


def upload_to_s3(directory:str, s3_bucket:str, s3_prefix:str, exclude_list:list, dry_run:bool=False, progress:bool=False, verbose:bool=False) -> None:
    """Upload file(s) from a directory to an S3 bucket.

    Args:
        directory (str): The directory containing file(s) to upload.
        s3_bucket (str): The name of the S3 bucket.
        s3_prefix (str): The prefix to use for S3 object keys.
        exclude_list (list): List of items to exclude from upload.
        dry_run (bool, optional): Simulate the upload process without actual upload. Defaults to False.
        verbose (bool, optional): Increase verbosity of the upload process. Defaults to False.
    """
    # if not s3_bucket or not s3_prefix:
    #     print("Error: Both --s3-bucket [S3_BUCKET] and --s3-prefix [S3_PREFIX] are required.")
    #     sys.exit(1)

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

        total_objects = get_total_upload_objects(directory, exclude_list)
        upload_size = get_total_upload_size(directory, exclude_list)
        print(f"Total Objects: {total_objects}")
        print(f"Total upload size: {format_size(upload_size)}")

        confirm = input("Proceed with upload? (yes/no): ").lower()
        if confirm == 'yes':
            state = load_state()

            uploaded_files = 0
            total_files = total_objects
            skipped_files = 0
            start_time = time.time()

            try:
                s3 = boto3.client('s3')
                for root, dirs, files in os.walk(directory):
                    dirs[:] = [d for d in dirs if d not in exclude_list]
                    for file in files:
                        if file not in exclude_list:
                            local_path = os.path.join(root, file)
                            relative_path = os.path.relpath(local_path, directory)
                            s3_key = os.path.join(s3_prefix, relative_path)
                            local_checksum = calculate_checksum(local_path)
                            file_size = os.path.getsize(local_path)
                            last_modified = os.path.getmtime(local_path)
                            # if local_path in state and local_checksum == state[local_path]['hash']:
                            if local_checksum == state[local_path]['hash']:
                                if verbose:
                                    print(f"Skipping {file} as it's already uploaded and unchanged.")
                                skipped_files += 1
                                continue
                            uploaded_files += 1
                            if progress:
                                if uploaded_files > skipped_files:
                                    progress_percentage = (uploaded_files / (total_files - skipped_files)) * 100
                                    remaining_files = total_files - uploaded_files
                                    time_elapsed = time.time() - start_time
                                    files_per_second = uploaded_files / time_elapsed
                                    time_remaining = remaining_files / files_per_second
                                    progress_line = f"Progress: {progress_percentage:.2f}% | Downloaded: {uploaded_files}/{total_files} | Remaining: {format_time(time_remaining)}"
                                else:
                                    progress_percentage = 0
                                    time_remaining = -1
                                    progress_line = f"Progress: {progress_percentage:.2f}% | Downloaded: {uploaded_files}/{total_files} | Remaining: N/A"
                                    sys.stdout.write("\r" + progress_line)
                                    sys.stdout.flush()

                                if dry_run:
                                    print(f"\nSimulating: Would upload {file} to S3 bucket {s3_bucket} as {s3_key}")
                                else:
                                    # print(f"Uploading {file} to S3 bucket {s3_bucket}")
                                    if verbose:
                                        print(f"\nUploading {local_path} to S3 bucket {s3_bucket} with key {s3_key}")
                                    s3.upload_file(local_path, s3_bucket, s3_key)
                                    last_modified_formated = datetime.utcfromtimestamp(last_modified).isoformat()
                                    state[local_path] = {'hash': local_checksum, 'size': file_size, 'last_modified': last_modified_formated, 'extension': os.path.splitext(file)[1]}
                                    if verbose:
                                        print(f"\nUploaded {file} as {s3_key}")
                save_state(state)
                print("\nUpload completed.")
            except (BotoCoreError, NoCredentialsError) as e:
                print(f"Error occurred: {e}")
        else:
            print("Upload operation canceled.")

    except KeyboardInterrupt:
        print("\nOperation interrupted by the user.")
        sys.exit(0)
