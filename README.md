# S3SyncUtility

**S3SyncUtility** is a Python tool using Boto3 to simplify syncing local directories with Amazon S3, for easy uploads and downloads.

## Prerequisites

- **Python 3.9 or higher**
- **Boto3** (Install using `pip install boto3`)
- **Configuration file parser** (Install using `pip install configparser`)

## Configuration (`.config.ini`)

The `.config.ini` file lets you customize your interaction with the S3 bucket.

### S3 Configuration

- `S3_BUCKET_NAME`: Name of your S3 bucket.
- `S3_PREFIX_TYPE`: Choose between "**internal**" or "**external**".
- `S3_PREFIX_CATEGORY`: Select from "**datasets**" or "**models**".
- `PROJECT_NAME`: Name of your project.
- `EXCLUDE` (optional): Specify files or directories to exclude.

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
