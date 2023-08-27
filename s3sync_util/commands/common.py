from datetime import datetime
import os
import boto3

from s3sync_util.commands.state_management import calculate_checksum
def get_total_upload_objects(directory, exclude_list):
    """Count the total number of objects (files and directories) in a directory.

    Args:
        directory (str): The directory to count objects in.
        exclude_list (list): List of items to exclude from counting.

    Returns:
        int: The total number of objects in the directory.
    """
    total_objects = 0
    for _, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_list]
        for file in files:
            if file not in exclude_list:
                total_objects += 1
    return total_objects

def get_total_download_objects(bucket, prefix):
    """Count the total number of objects (files and directories) in an S3 bucket with a given prefix.

    Args:
        bucket (str): The name of the S3 bucket.
        prefix (str): The prefix to filter objects by.

    Returns:
        int: The total number of objects in the S3 bucket with the given prefix.
    """
    s3 = boto3.client('s3')

    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    total_objects = len(response.get('Contents', []))
    return total_objects

def format_time(seconds):
    """Format seconds into a string representation of time in HH:MM:SS format.

    Args:
        seconds (int): The total number of seconds.

    Returns:
        str: A formatted string representation of time in HH:MM:SS format.
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
