from s3sync_util.commands.common import config
from botocore.client import BaseClient
from typing import Union


def multipart_upload_to_s3(local_file_path: str, s3: BaseClient, bucket_name: str, object_key: str):
    """
    Uploads a local file to S3 using multipart upload.

    Args:
        local_file_path (str): The path to the local file to be uploaded.
        s3 (BaseClient): An instance of the boto3 S3 client or resource.
        object_key (str): The desired key for the uploaded object in the bucket.
    """
    if isinstance(s3, BaseClient):
        s3_client = s3
    else:
        raise ValueError("s3 must be an instance of boto3 S3 client or resource")

    # Initialize multipart upload
    response = s3_client.create_multipart_upload(Bucket=bucket_name, Key=object_key)
    upload_id = response['UploadId']

    # Calculate part size
    part_size = 5 * 1024 * 1024  # 5 MB

    # Prepare parts
    with open(local_file_path, 'rb') as file:
        parts = []
        part_number = 1
        while True:
            data = file.read(part_size)
            if not data:
                break
            part_response = s3_client.upload_part(
                Bucket=bucket_name,
                Key=object_key,
                PartNumber=part_number,
                UploadId=upload_id,
                Body=data
            )
            parts.append({'PartNumber': part_number, 'ETag': part_response['ETag']})
            part_number += 1

    # Complete multipart upload
    s3_client.complete_multipart_upload(
        Bucket=bucket_name,
        Key=object_key,
        UploadId=upload_id,
        MultipartUpload={'Parts': parts}
    )

def multipart_download_from_s3(local_file_path: str, s3: BaseClient, bucket_name: str, object_key: str, total_size: int):
    """
    Downloads an object from S3 using multipart download.

    Args:
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The key of the object to be downloaded.
        local_file_path (str): The desired path for the downloaded file.
        s3 (BaseClient): An instance of the boto3 S3 client or resource.
    """
    if isinstance(s3, BaseClient):
        s3_client = s3
    else:
        raise ValueError("s3 must be an instance of boto3 S3 client or resource")

    # Get object information to determine the total size
    # response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
    # total_size = response['ContentLength']

    # Calculate part size
    part_size = 5 * 1024 * 1024  # 5 MB

    # Download parts
    with open(local_file_path, 'wb') as file:
        for part_number in range(1, total_size // part_size + 1):
            start_byte = (part_number - 1) * part_size
            end_byte = min(part_number * part_size, total_size) - 1
            response = s3_client.get_object(
                Bucket=bucket_name,
                Key=object_key,
                Range=f"bytes={start_byte}-{end_byte}"
            )
            file.write(response['Body'].read())