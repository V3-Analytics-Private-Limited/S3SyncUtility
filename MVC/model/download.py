#download


def download_from_s3(s3_bucket: str, s3_prefix: str, directory: str, exclude_list: list, dry_run: bool=False, progress: bool=False, verbose: bool=False) -> None:
    """Download files(s) from an S3 bucket to a local directory."""
    """This method perform by when the method is called by the controller"""

    """Args:
        s3_bucket (str): The name of the S3 bucket.
        s3_prefix (str): The prefix to filter S3 objects.
        local_dir (str): The local directory to save downloaded file(s).
        exclude_list (list): List of items to exclude from download.
        dry_run (bool, optional): Simulate the download process without actual download. Defaults to False.
        progress (bool, optional): Display progress statistics. Defaults to False.
        verbose (bool, optional): Increase verbosity of the download process. Defaults to False."""
  

