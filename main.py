import hashlib
import os
import boto3
import argparse

def calculate_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def upload_to_s3(local_dir, s3_bucket, s3_prefix):
    s3 = boto3.client('s3')

    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_dir)
            s3_key = os.path.join(s3_prefix, relative_path)
            print(f"Uploading {file} to S3 bucket {s3_bucket}")
            s3.upload_file(local_path, s3_bucket, s3_key)

def download_from_s3(s3_bucket, s3_prefix, local_dir):
    s3 = boto3.client('s3')

    response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
    for obj in response.get('Contents', []):
        s3_key = obj['Key']
        local_path = os.path.join(local_dir, os.path.relpath(s3_key, s3_prefix))
        print(f"Downloading {s3_key} from S3 bucket {s3_bucket}")
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3.download_file(s3_bucket, s3_key, local_path)


def main():
    parser = argparse.ArgumentParser(description="Upload and download directories/files from Amazon S3")
    parser.add_argument("--upload", help="Upload directories/files to S3", action="store_true")
    parser.add_argument("--download", help="Download directories/files from S3", action="store_true")
    args = parser.parse_args()

    local_dir = './'
    s3_bucket = ''
    s3_prefix = ''

    if args.upload:
        upload_to_s3(local_dir, s3_bucket, s3_prefix)
        print("Upload process completed.")

    elif args.download:
        download_from_s3(s3_bucket, s3_prefix, local_dir)
        print("Download process completed.")

if __name__ == "__main__":
    main()