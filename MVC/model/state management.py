#state management

def calculate_checksum(file_path:str, block_size:int=4096) -> str:
    """Calculate the MD5 checksum of a file."""
    """This function called by upload file in the model"""
    pass

def load_state() -> dict:
    """Load the state from a JSON file."""
    """This method called by both upload and download files in the model"""
    pass

def save_state(state:dict) -> None:
    """Save the state to a JSON file."""
    """his method called by both upload and download files in the model"""
    pass


