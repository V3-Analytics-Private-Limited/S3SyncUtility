# S3SyncUtility

S3SyncUtility is a Python script that enables you to easily upload and download directories to and from Amazon S3. This script uses the Boto3 library to interact with S3, allowing you to synchronize your local directories with S3 buckets in an incremental manner.

## Prerequisites

- Python ^3.9
- Boto3 (install using `pip install boto3`)
- Configuration file parser (install using `pip install configparser`)

## Configuration (`.config.ini`)

The `.config.ini` file allows you to customize how your project interacts with the S3 bucket.

### S3 Configuration

- `S3_BUCKET_NAME`: Name of your S3 bucket.
- `S3_PREFIX_TYPE`: Set to **`internal`** or **`external`**.
- `S3_PREFIX_CATEGORY`: Choose **`datasets`** or **`models`**.
- `PROJECT_NAME`: Your project's name.
- `EXCLUDE` (optional): Files or directories to exclude.

**Example:**

```ini
[S3_CONFIG]
S3_BUCKET_NAME=my-bucket
S3_PREFIX_TYPE=internal
S3_PREFIX_CATEGORY=datasets
PROJECT_NAME=my_project
EXCLUDE=file1,dir2
```

## Usage

To use the script, run it from the command line with the following options:

```bash
python main.py --upload
python main.py --download
```

## Command-line Arguments

- `--upload`: Upload directories/files to Amazon S3.

- `--download`: Download directories/files from Amazon S3.

- `--exclude`: Exclude specific files or directories from upload/download. 

**Example:**

```bash
python main.py --upload --exclude file1 dir2
```

This will upload directories/files to Amazon S3 while excluding `file1` and `dir2`.