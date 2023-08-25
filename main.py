import hashlib
import os
import sys
import argparse

try:
    import boto3
    from configparser import ConfigParser
except ModuleNotFoundError as e:
    missing_module = str(e).split("'")[1]
    print(f"Error: This script requires the '{missing_module}' module. Please install it using 'pip install {missing_module}'")
    sys.exit(1)

def calculate_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_total_objects(directory, exclude_list):
    total_objects = 0
    for _, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_list]
        for file in files:
            if file not in exclude_list:
                total_objects += 1
    return total_objects

def get_total_objects_s3(bucket, prefix):
    s3 = boto3.client('s3')

    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    total_objects = len(response.get('Contents', []))
    return total_objects

def upload_to_s3(directory, s3_bucket, s3_prefix, exclude_list, dry_run=False):
    s3 = boto3.client('s3')

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_list]
        for file in files:
            if file not in exclude_list:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, directory)
                s3_key = os.path.join(s3_prefix, relative_path)
                
                if dry_run:
                    print(f"Simulating: Would upload {file} to S3 bucket {s3_bucket} as {s3_key}")
                else:
                    print(f"Uploading {file} to S3 bucket {s3_bucket}")
                    s3.upload_file(local_path, s3_bucket, s3_key)

def download_from_s3(s3_bucket, s3_prefix, local_dir, exclude_list, dry_run=False):
    s3 = boto3.client('s3')

    response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
    for obj in response.get('Contents', []):
        s3_key = obj['Key']
        if not any(item in s3_key for item in exclude_list):
            local_path = os.path.join(local_dir, os.path.relpath(s3_key, s3_prefix))
            
            if dry_run:
                print(f"Simulating: Would download {s3_key} from S3 bucket {s3_bucket} to {local_path}")
            else:
                print(f"Downloading {s3_key} from S3 bucket {s3_bucket}")
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                s3.download_file(s3_bucket, s3_key, local_path)

def main():
    parser = argparse.ArgumentParser(description="Upload and download directories/files from Amazon S3")
    parser.add_argument("--upload", help="Upload directories/files to S3", action="store_true")
    parser.add_argument("--download", help="Download directories/files from S3", action="store_true")
    parser.add_argument("--dry-run", help="Simulate the operation without actual upload/download", action="store_true")
    parser.add_argument("--exclude", nargs='*', help="Exclude files or directories from upload/download", default=[])
    args = parser.parse_args()

    directory = os.getcwd() # os.path.dirname(os.path.realpath(__file__))

    try:
        config = ConfigParser()
        config.read(os.path.join(directory, '.config.ini'))    
        s3_bucket = config.get('S3_CONFIG', 'S3_BUCKET_NAME')
        s3_prefix_type = config.get('S3_CONFIG', 'S3_PREFIX_TYPE')
        s3_prefix_category = config.get('S3_CONFIG', 'S3_PREFIX_CATEGORY')
        project_name = config.get('S3_CONFIG', 'PROJECT_NAME')
        ignored_items = [item.strip() for item in config.get('S3_CONFIG', 'EXCLUDE', fallback='').split(',')]

    except Exception:
        print("Error: Please make sure the .config.ini file is correctly configured with [S3_CONFIG] section.")
        sys.exit(1)

    s3_prefix = f"{s3_prefix_type}/{s3_prefix_category}/{project_name}"

    exclude_list = args.exclude + ignored_items + ['main.py', '.config.ini', '.git']

    if args.upload:
        print("Uploading to S3:")
        print(f"Bucket: {s3_bucket}")
        print(f"Uploading To: {s3_prefix_type}/{s3_prefix_category}")
        print(f"Total Objects: {get_total_objects(directory, exclude_list)}")
        confirm = input("Proceed with upload? (yes/no): ").lower()
        if confirm == 'yes':
            upload_to_s3(directory, s3_bucket, s3_prefix, exclude_list, args.dry_run)
            if not args.dry_run:
                print("Upload process completed.")
        else:
            print("Upload operation canceled.")

    elif args.download:
        print("Downloading from S3:")
        print(f"Bucket: {s3_bucket}")
        print(f"Downloading From: {s3_prefix_type}/{s3_prefix_category}")
        print(f"Total Objects: {get_total_objects_s3(s3_bucket, s3_prefix)}")
        confirm = input("Proceed with download? (yes/no): ").lower()
        if confirm == 'yes':
            download_from_s3(s3_bucket, s3_prefix, directory, exclude_list, args.dry_run)
            if not args.dry_run:
                print("Download process completed.")
        else:
            print("Download operation canceled.")

if __name__ == "__main__":
    main()