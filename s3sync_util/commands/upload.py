import sys
import os
import boto3
import time
from datetime import datetime
from ..logger import logger
from botocore.exceptions import BotoCoreError, NoCredentialsError
from s3sync_util.commands.multipart import multipart_upload_to_s3
from s3sync_util.commands.size import get_total_upload_size, format_size
from s3sync_util.commands.common import get_total_upload_objects, format_time, config
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
            logger.error("Both --s3-bucket [S3_BUCKET] and --s3-prefix [S3_PREFIX] are required (1).")
            print("Error: Both --s3-bucket [S3_BUCKET] and --s3-prefix [S3_PREFIX] are required.")
        elif not s3_bucket:
            logger.error("--s3-bucket [S3_BUCKET] is required (1).")
            print("Error: --s3-bucket [S3_BUCKET] is required.")
        else:
            logger.error("--s3-prefix [S3_PREFIX] is required (1).")
            print("Error: --s3-prefix [S3_PREFIX] is required.")
        logger.critical("process exited due to error code 1 (1).")
        sys.exit(1)

    try:
        print("Uploading to S3:")
        print(f"Bucket: {s3_bucket}")
        print(f"Uploading To: {s3_prefix}")
        logger.info("Uploading from S3.")

        total_objects = get_total_upload_objects(directory, exclude_list)
        upload_size = get_total_upload_size(directory, exclude_list)
        print(f"Total Objects: {total_objects}")
        logger.info(f"no of object in the directory ,{total_objects}.")
        print(f"Total upload size: {format_size(upload_size)}")

        confirm = input("Proceed with upload? (yes/no): ").lower()
        if confirm == 'yes':
            logger.info("user select yes (1)")
            state = load_state()
            logger.info(f"The loaded state as a dictionary {state} (1).")
            uploaded_files = 0
            total_files = total_objects
            skipped_files = 0
            start_time = time.time()
            logger.info(f"Upload start time {start_time} .")

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
                            logger.info(f"MD5 checksum of the file {local_checksum}(0).")

                            file_size = os.path.getsize(local_path)
                            logger.info(f"getting file size for upload {file_size}.")
                            last_modified = os.path.getmtime(local_path)
                            logger.info(f"modification time of a file {last_modified}.")
                            # if local_path in state and local_checksum == state[local_path]['hash']:
                            if local_checksum in state:
                            # if state.get(local_path, {}).get('hash') == local_checksum:
                                if verbose:
                                    logger.info("Skipping file as it's already uploaded and unchanged.")
                                    print(f"Skipping {file} as it's already uploaded and unchanged.")
                                skipped_files += 1
                                continue
                            uploaded_files += 1
                            if uploaded_files > skipped_files:
                                progress_percentage = (uploaded_files / (total_files - skipped_files)) * 100
                                remaining_files = total_files - uploaded_files
                                time_elapsed = time.time() - start_time
                                files_per_second = uploaded_files / time_elapsed
                                time_remaining = remaining_files / files_per_second
                                progress_line = f"Progress: {progress_percentage:.2f}% | Uploaded: {uploaded_files}/{total_files} | Remaining: {format_time(time_remaining)}"
                                logger.info(f"Uploading process, {progress_line} (0).")
                            else:
                                progress_percentage = 0
                                time_remaining = -1
                                progress_line = f"Progress: {progress_percentage:.2f}% | Uploaded: {uploaded_files}/{total_files} | Remaining: N/A"
                                logger.info(f"Uploading process, {progress_line} (1).")
                            if progress:
                                sys.stdout.write("\r" + progress_line)       
                                sys.stdout.flush()

                            if dry_run:
                                logger.info("Simulating: Would upload file to S3 bucket as s3_key.")
                                print(f"\nSimulating: Would upload {file} to S3 bucket {s3_bucket} as {s3_key}")
                            else:
                                # print(f"Uploading {file} to S3 bucket {s3_bucket}")
                                logger.info("Uploading file to S3 bucket")

                                if verbose:
                                    logger.info("Uploading local_path to S3 bucket with key s3_key")
                                    print(f"\nUploading {local_path} to S3 bucket {s3_bucket} with key {s3_key}")
                                if file_size >= 100_000_000: # 100 MB
                                    logger.warning("file's size is over 100 MB, using multipart upload for better transfer efficiency.")
                                    print(f"\n{file}'s size is over 100 MB, using multipart upload for better transfer efficiency.")
                                    multipart_upload_to_s3(local_path, s3, s3_bucket, s3_key)
                                
                                else:
                                    s3.upload_file(local_path, s3_bucket, s3_key, Config=config)
                                last_modified_formated = datetime.utcfromtimestamp(last_modified).isoformat()
                                state[local_checksum] = {'file': local_path, 'size': file_size, 'last_modified': last_modified_formated, 'extension': os.path.splitext(file)[1]}
                                if verbose:
                                    print(f"\nUploaded {file} as {s3_key}")
                save_state(state)
                logger.info("Upload completed.")
                print("\nUpload completed.")
            except (BotoCoreError, NoCredentialsError) as e:
                logger.error(f"Error occurred: {e} (2)")
                print(f"Error occurred: {e}")
        else:
            logger.critical("Upload operation canceled due to user select no.")
            print("Upload operation canceled.")

    except KeyboardInterrupt:
        logger.critical("Operation interrupted due to KeyboardInterrupt (2).")
        print("\nOperation interrupted by the user.")
        sys.exit(0)
