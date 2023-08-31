import os
from configparser import ConfigParser
from ..logger import logger

def load_configuration():
    """Load configuration from a .config.ini file.

    Returns:
        ConfigParser: A ConfigParser instance containing the loaded configuration.
    """
    config = ConfigParser()
    config_file_path = os.path.join(os.getcwd(), ".config.ini")
    config.read(config_file_path)
    logger.info("load configuration successfully ")
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

        logger.warning(f"message :{e}")
        print(f"Warning: {e}\nNo valid configuration found. Use 's3sync config init' or provide flags.\nDefaults applied.\n")
        # s3_bucket, s3_prefix_type, s3_prefix_category, project_name, ignored_items = '', '', '', '', []
        s3_bucket, s3_prefix, ignored_items = '', '', []        

    # s3_prefix = f"{s3_prefix_type}/{s3_prefix_category}/{project_name}" if s3_bucket else ""
    exclude_list = ignored_items + ['.config.ini', '.git', '.state.json']

    logger.info("stored s3_bucket , s3_prefix and exclude_list")
    return s3_bucket, s3_prefix, exclude_list

def init_config_interactive():
    """Interactively creates the .config.ini file based on user input."""
    try:
        config = ConfigParser()

        s3_bucket_name = input("Enter S3 bucket name: ")
        logger.info("Takes s3_bucket_name from user")
        # s3_prefix_type = input("Enter S3 prefix type: ")
        # s3_prefix_category = input("Enter S3 prefix category: ")
        # project_name = input("Enter project name: ")
        s3_prefix = input("Enter S3 prefix: ")
        logger.info("Takes s3_prefix from user")

        exclude = input("Enter excluded items (comma-separated): ")
        logger.info("Takes exclude items from user")

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

        logger.info(".config.ini file created successfully!")
        print(".config.ini file created successfully!")

    except KeyboardInterrupt:

        logger.critical("Operation canceled by user due to KeyboardInterrupt (0)")
        print("\nOperation canceled by user.")
    except Exception as e:
        logger.error(f"error :{e}")
        print(f"An error occurred: {e} (0)")
