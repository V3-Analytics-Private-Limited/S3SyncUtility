import argparse
import os
import sys

from s3sync_util.config import utils
from s3sync_util.commands import upload, download


def main():
    """Main entry point for the S3Sync utility."""
    parser = argparse.ArgumentParser(description="Upload and download directories/files from Amazon S3")
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand', description="Available subcommands for managing S3Sync:")

    config_parser = subparsers.add_parser(
        'config',
        help='Manage the S3Sync configuration',
        description='Configure various settings such as access credentials, default storage locations, and synchronization options. This command serves as the foundation for tailoring S3Sync to your specific needs, ensuring seamless integration with your workflow.'
    )

    config_parser.add_argument("init", help="Interactively create .config.ini")
    config_parser.set_defaults(func=utils.init_config_interactive)

    directory = os.getcwd()
    s3_bucket, s3_prefix, exclude_list = utils.load_s3_config()

    upload_parser = subparsers.add_parser(
        'upload',
        help='Upload directories/files to S3',
        description='Seamlessly upload directories and files to Amazon S3. Whether you\'re backing up important data or distributing assets, this command streamlines the process by securely transferring your content to the cloud. You can define upload options, such as storage classes and encryption, to align with your data management strategies.'
    )

    upload_parser.add_argument("--directory", help="Local directory to upload", default=directory)
    upload_parser.add_argument("--s3-bucket", help="S3 bucket to upload to", default=s3_bucket)
    upload_parser.add_argument("--s3-prefix", help="Prefix to use for S3 object keys", default=s3_prefix)
    upload_parser.add_argument("--exclude", nargs='*', help="Exclude files or directories from upload", default=[])
    upload_parser.add_argument("--dry-run", help="Simulate the upload process", action="store_true")
    upload_parser.add_argument("--progress", help="Display progress statistics.", action="store_true")
    upload_parser.add_argument("--verbose", help="Verbosity of the upload process", action="store_true")
    upload_parser.set_defaults(func=lambda args: upload.upload_to_s3(
        args.directory, args.s3_bucket, args.s3_prefix, args.exclude + exclude_list, args.dry_run, args.progress, args.verbose
    ))

    download_parser = subparsers.add_parser(
        'download',
        help='Download directories/files from S3',
        description='Effortlessly retrieve directories and files from Amazon S3 to your local environment. Whether you\'re restoring backups or accessing shared resources, this command simplifies the retrieval process. Customize download preferences such as overwriting rules and filtering to ensure you have the right files where you need them.'
    )

    download_parser.add_argument("--s3-bucket", help="S3 bucket to download from", default=s3_bucket)
    download_parser.add_argument("--s3-prefix", help="Prefix to use for S3 object keys", default=s3_prefix)
    download_parser.add_argument("--directory", help="Local directory to save downloaded files", default=directory)
    download_parser.add_argument("--exclude", nargs='*', help="Exclude files or directories from download", default=[])
    download_parser.add_argument("--dry-run", help="Simulate the download process", action="store_true")
    download_parser.add_argument("--progress", help="Display progress statistics.", action="store_true")
    download_parser.add_argument("--verbose", help="Verbosity of the download process", action="store_true")
    download_parser.set_defaults(func=lambda args: download.download_from_s3(
        args.s3_bucket, args.s3_prefix, args.directory, args.exclude + exclude_list, args.dry_run, args.progress, args.verbose
    ))

    args = parser.parse_args()

    if args.subcommand == 'config':
        if hasattr(args, 'func'):
            args.func()
    elif hasattr(args, 'func'):
        try:
            args.func(args)
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()