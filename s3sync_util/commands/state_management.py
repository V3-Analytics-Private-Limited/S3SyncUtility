import os
import json
import hashlib

def calculate_checksum(file_path:str, block_size:int=4096) -> str:
    """Calculate the MD5 checksum of a file.

    Args:
        file_path (str): The path to the file.
        block_size (int, optional): Size of data blocks for checksum calculation. Default is 8192 bytes.

    Returns:
        str: The MD5 checksum of the file.
    """
    checksum = hashlib.md5()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            checksum.update(block)
    return checksum.hexdigest()

def load_state() -> dict:
    """
    Load the state from a JSON file.

    Returns:
        dict: The loaded state as a dictionary. If the file doesn't exist, an empty dictionary is returned.
    """
    state_file_path = os.path.join(os.getcwd(), '.state.json')
    try:
        if os.path.exists(state_file_path):
            with open(state_file_path, 'r') as state_file:
                return json.load(state_file)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error occurred while loading state: {e}")

    # If the file doesn't exist or there's an error, return an empty dictionary
    return {}

def save_state(state:dict) -> None:
    """
    Save the state to a JSON file.

    Args:
        state (dict): The state to be saved as a dictionary.
    """
    state_file_path = os.path.join(os.getcwd(), '.state.json')
    try:
        with open(state_file_path, 'w') as state_file:
            json.dump(state, state_file, indent=4)
    except IOError as e:
        print(f"Error occurred while saving state: {e}")