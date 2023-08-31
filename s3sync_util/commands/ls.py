import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError

def list_s3_contents(s3_bucket: str, path: str):
    """
    List the contents of a specified path within an S3 bucket.

    Args:
        s3_bucket (str): The name of the S3 bucket.
        path (str): The path within the S3 bucket to list contents from.
    """
    try:
        s3_client = boto3.client('s3')

        response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=path)

        if 'Contents' in response:
            print(f"Contents of '{path}' in bucket '{s3_bucket}':")
            for obj in response['Contents']:
                print(obj['Key'])
        else:
            print(f"No contents found in '{path}' in bucket '{s3_bucket}'.")

    except (BotoCoreError, NoCredentialsError) as e:
        print(f"Error occurred: {e}")