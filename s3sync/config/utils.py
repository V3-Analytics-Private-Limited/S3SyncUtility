import os
from configparser import ConfigParser

def load_configuration():
    """Load configuration from a .config.ini file.

    Returns:
        ConfigParser: A ConfigParser instance containing the loaded configuration.
    """
    config = ConfigParser()
    config_file_path = os.path.join(os.getcwd(), ".config.ini")
    config.read(config_file_path)
    return config

def load_s3_config():
    try:
        config = load_configuration()
        s3_bucket = config.get('S3_CONFIG', 'S3_BUCKET_NAME')
        # s3_prefix_type = config.get('S3_CONFIG', 'S3_PREFIX_TYPE')
        # s3_prefix_category = config.get('S3_CONFIG', 'S3_PREFIX_CATEGORY')
        # project_name = config.get('S3_CONFIG', 'PROJECT_NAME')
        s3_prefix = config.get('S3_CONFIG', 'S3_PREFIX')
        ignored_items = [item.strip() for item in config.get('S3_CONFIG', 'EXCLUDE', fallback='').split(',')]
    except Exception as e:
        print(f"Warning: {e}\nNo valid configuration found. Use 's3sync config init' or provide flags.\nDefaults applied.\n")
        # s3_bucket, s3_prefix_type, s3_prefix_category, project_name, ignored_items = '', '', '', '', []
        s3_bucket, s3_prefix, ignored_items = '', '', []        

    # s3_prefix = f"{s3_prefix_type}/{s3_prefix_category}/{project_name}" if s3_bucket else ""
    exclude_list = ignored_items + ['.config.ini', '.git', '.state.json']

    return s3_bucket, s3_prefix, exclude_list

def init_config_interactive():
    """Interactively creates the .config.ini file based on user input."""
    try:
        config = ConfigParser()

        s3_bucket_name = input("Enter S3 bucket name: ")
        # s3_prefix_type = input("Enter S3 prefix type: ")
        # s3_prefix_category = input("Enter S3 prefix category: ")
        # project_name = input("Enter project name: ")
        s3_prefix = input("Enter S3 prefix: ")
        exclude = input("Enter excluded items (comma-separated): ")

        config['S3_CONFIG'] = {
            'S3_BUCKET_NAME': s3_bucket_name,
            # 'S3_PREFIX_TYPE': s3_prefix_type,
            # 'S3_PREFIX_CATEGORY': s3_prefix_category,
            # 'PROJECT_NAME': project_name,
            'S3_PREFIX': s3_prefix,
            'EXCLUDE': exclude
        }

        config_file_path = os.path.join(os.getcwd(), '.config.ini')
        with open(config_file_path, 'w') as config_file:
            config.write(config_file)

        print(".config.ini file created successfully!")

    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
