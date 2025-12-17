from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import base64
import os


def xor_encode(s, key=42):
    xor_str = ''.join(chr(ord(c) ^ key) for c in s)
    encoded_bytes = base64.b64encode(xor_str.encode('utf-8'))
    return encoded_bytes.decode('utf-8')


def get_save_path(save_path: str = None) -> str:
    """
    Get the path where the file should be saved.

    Args:
        save_path (str, optional): The path to save the file.

    Returns:
        str: The path where the file is saved.
    
    Raises:
        ValueError: If save_path does not end with a '/'.
    """
    # If save_path is provided, check if it ends with a '/'
    if save_path and save_path.endswith('/'):
        return f'{save_path}'
    
    if save_path and not save_path.endswith('/'):
        raise ValueError("save_path must end with a '/'")
    
    return os.getcwd() + '/'


def get_unique_filename(save_path: str, file_name: str) -> str:
    base, ext = os.path.splitext(file_name)
    counter = 1
    new_file = f"{save_path}{base}({counter}){ext}"
    while os.path.exists(new_file):
        new_file = f"{save_path}{base}({counter}){ext}"
        counter += 1
    return new_file


def clean_data(data: dict) -> dict:
    """
    Cleans the input data by removing keys with None values.

    Args:
        data (dict): The input data.

    Returns:
        dict: The cleaned data.
    """
    return {k: v for k, v in data.items() if v is not None}

def join_url_params(base_url: str, params: dict) -> str:
    """
    Join URL with parameters while preserving existing query parameters.
    
    Args:
        base_url (str): Base URL that may contain existing parameters
        params (dict): New parameters to add
        
    Returns:
        str: URL with all parameters properly joined
    """
    # Parse the URL
    parsed = urlparse(base_url)
    
    # Get existing parameters
    existing_params = parse_qs(parsed.query)
    
    # Update with new parameters
    existing_params.update(params)
    
    # Reconstruct the URL
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(existing_params, doseq=True),
        parsed.fragment
    ))