#size

def get_total_upload_size(directory:str, exclude_list:list) -> int:
    """Calculate the total size of files in a directory for upload, excluding specified files."""
    """This function called by upload file in the model"""
    pass

def get_total_download_size(s3_bucket:str, s3_prefix:str, exclude_list:list) -> int:
    """Calculate the total size of objects to be downloaded from an S3 bucket and prefix."""
    """This function called by upload file in the model"""
    pass

def format_size(size_in_bytes:int) -> float:
    """It used to calculate the ssize format which as bytes, KB or MB or GB """
    """This function called by both download and upload files in the model"""
    pass 



 
