import os
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError

def get_total_upload_size(directory, exclude_list):
    """Calculate the total size of files in a directory for upload, excluding specified files.

    Args:
        directory (str): The directory to calculate the upload size for.
        exclude_list (list): List of items to exclude from the upload size calculation.

    Returns:
        int: Total size of files in bytes.
    """
    total_size = 0

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_list]
        for file in files:
            if file not in exclude_list:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)

    return total_size

def get_total_download_size(s3_bucket, s3_prefix, exclude_list):
    """Calculate the total size of objects to be downloaded from an S3 bucket and prefix.

    Args:
        s3_bucket (str): The name of the S3 bucket.
        s3_prefix (str): The prefix to filter S3 objects.
        exclude_list (list): List of items to exclude.

    Returns:
        int: Total size of objects in bytes.
    """
    total_size = 0

    try:
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
        for obj in response.get('Contents', []):
            s3_key = obj['Key']
            if not any(item in s3_key for item in exclude_list):
                total_size += obj['Size']
    except (BotoCoreError, NoCredentialsError) as e:
        print(f"Error occurred: {e}")
    return total_size

def format_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"