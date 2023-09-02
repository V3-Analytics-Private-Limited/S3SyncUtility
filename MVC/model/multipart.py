#multipart

def multipart_upload_to_s3(local_file_path: str, s3: BaseClient, bucket_name: str, s3_prefix: str):
    """Uploads a local file to S3 using multipart upload."""

    """this function is called by upload file in model only the file size is above 100mb"""
    pass

def multipart_download_from_s3(local_file_path: str, s3: BaseClient, bucket_name: str, s3_prefix: str, total_size: int) -> None:
    """Downloads an object from S3 using multipart download."""
    
    """this function is called by download file in model only the file size is above 100mb"""
    pass

