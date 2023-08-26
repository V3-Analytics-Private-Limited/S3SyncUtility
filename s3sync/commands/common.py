import os
import hashlib
import boto3

def calculate_checksum(file_path):
    """Calculate the MD5 checksum of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The MD5 checksum of the file.
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_total_objects(directory, exclude_list):
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

def get_total_objects_s3(bucket, prefix):
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