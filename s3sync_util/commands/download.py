import sys
import os
import time
import boto3
from ..logger import logger
from botocore.exceptions import BotoCoreError, NoCredentialsError
from s3sync_util.commands.multipart import multipart_download_from_s3
from s3sync_util.commands.state_management import load_state, save_state
from s3sync_util.commands.size import get_total_download_size, format_size
from s3sync_util.commands.common import get_total_download_objects, format_time, config


def download_from_s3(s3_bucket: str, s3_prefix: str, directory: str, exclude_list: list, dry_run: bool=False, progress: bool=False, verbose: bool=False) -> None:
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
            logger.error("Both --s3-bucket [S3_BUCKET] and --s3-prefix [S3_PREFIX] are required (0).")
            print("Error: Both --s3-bucket [S3_BUCKET] and --s3-prefix [S3_PREFIX] are required.")
        elif not s3_bucket:
            logger.error("--s3-bucket [S3_BUCKET] is required (0).")
            print("Error: --s3-bucket [S3_BUCKET] is required.")
        else:
            logger.error("--s3-prefix [S3_PREFIX] is required (0).")
            print("Error: --s3-prefix [S3_PREFIX] is required.")

        logger.critical("process exited due to error code 1 (0).")
        sys.exit(1)

    try:
        
        print("Downloading from S3:")
        print(f"Bucket: {s3_bucket}")
        print(f"Downloading From: {s3_prefix}.")
        logger.info("Downloading from S3.")

        total_objects = get_total_download_objects(s3_bucket, s3_prefix)
        download_size = get_total_download_size(s3_bucket, s3_prefix, exclude_list)
        get_download_size=format_size(download_size)

        print(f"Total Objects: {total_objects}.")
        logger.info(f"no of object in the s3 bucket , {total_objects}.")

        print(f"Total download size: {get_download_size}.")
        logger.info(f"Total download size: {get_download_size}.")

        confirm = input("Proceed with download? (yes/no): ").lower()
        logger.info("Takes yes or no from user to procees the download.")

        if confirm == 'yes':
            logger.info("user select yes (0)")
            state = load_state()
            logger.info(f"The loaded state as a dictionary {state} (0).")
            downloaded_files = 0
            total_files = total_objects
            skipped_files = 0
            start_time = time.time()
            logger.info(f"Download start time {start_time} .")
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
                                    logger.info("kipping {s3_key} as it's already downloaded and unchanged.")
                                    print(f"Skipping {s3_key} as it's already downloaded and unchanged.")
                                skipped_files += 1
                                continue

                        logger.info("Download Starts")    
                        # Download the file(s)
                        downloaded_files += 1
                        if downloaded_files > skipped_files:
                            progress_percentage = (downloaded_files / (total_files - skipped_files)) * 100
                            remaining_files = total_files - downloaded_files
                            time_elapsed = time.time() - start_time
                            files_per_second = downloaded_files / time_elapsed
                            time_remaining = remaining_files / files_per_second
                            progress_line = f"Progress: {progress_percentage:.2f}% | Downloaded: {downloaded_files}/{total_files} | Remaining: {format_time(time_remaining)}"
                            logger.info(f"Downloading process, {progress_line} (0).")
                        else:
                            progress_percentage = 0
                            time_remaining = -1
                            progress_line = f"Progress: {progress_percentage:.2f}% | Downloaded: {downloaded_files}/{total_files} | Remaining: N/A"
                            logger.info(f"Downloading process, {progress_line} (1).")

                        if progress:
                            sys.stdout.write("\r" + progress_line)
                            sys.stdout.flush()
                        if dry_run:
                            logger.info("Simulating: Would download s3_key from S3 bucket to local_path.")
                            print(f"\nSimulating: Would download {s3_key} from S3 bucket {s3_bucket} to {local_path}")
                        else:
                            # print(f"Downloading {s3_key} from S3 bucket {s3_bucket}")
                            logger.info("Downloading s3_key from S3 bucket s3_bucket.")

                            if verbose:
                                print(f"S3 Key: {s3_key}")
                                print(f"Local Path: {local_path}")
                            os.makedirs(os.path.dirname(local_path), exist_ok=True)
                            response = s3.head_object(Bucket=s3_bucket, Key=s3_key)
                            total_size = response['ContentLength']
                            if total_size >= 100_000_000: # 100 MB

                                logger.warning("size is over 100 MB, using multipart download for better transfer efficiency.")
                                print(f"\n{s3_key}'s size is over 100 MB, using multipart download for better transfer efficiency.")
                                multipart_download_from_s3(local_path, s3, s3_bucket, s3_key, total_size)
                            else:
                                logger.info("File size less tha n 100mb")
                                s3.download_file(s3_bucket, s3_key, local_path, Config=config)
                            if verbose:
                                logger.info("Downloaded s3_key as local_path")
                                print(f"\nDownloaded {s3_key} as {local_path}")
                            state[remote_etag] = {'file': local_path, 'last_modified': last_modified.isoformat(), 'extension': os.path.splitext(s3_key)[-1]}
                save_state(state)
                logger.info("Download complete.")
                print("\nDownload completed.")
            except (BotoCoreError, NoCredentialsError) as e:
                logger.error(f"error :{e} (1).")
                print(f"Error occurred: {e}.")
        else:
            logger.critical("Download operation canceled.")
            print("Download operation canceled due to user select no.")

    except KeyboardInterrupt:
        logger.critical("Operation interrupted by the user due to KeyboardInterrupt (1).")
        print("\nOperation interrupted by the user.")
        sys.exit(0)
