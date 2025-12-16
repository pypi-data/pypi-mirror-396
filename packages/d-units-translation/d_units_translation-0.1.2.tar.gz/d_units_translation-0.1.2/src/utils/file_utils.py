import logging
import json
import os

def create_json_file(filepath: str) -> None:
    """
    Create an empty JSON file inside the given directory.

    Args:
        filepath (str): Filepath where the temporary file will be created
    
    Raises:
        OSERROR: If the file cannot be created.
    """    
    if os.path.exists(filepath):
        logging.info(f"File already exists: {filepath} creation skipped.")
        return
    
    try:
        with open(filepath, 'w'):
            logging.info(f"Created: {filepath}")
            pass

    except OSError as e:
        raise OSError(f"Failed to create file '{filepath}': {e}") from e


def load_json(path: str, surpress_empty_file_log: bool = False) -> tuple[list[dict], int]:
    """
    Loads the JSON file from the given path and returns its contents as a list[dict]
    along with the number of rows. If the file is empty, returns an empty list
    and a count of 0. All other exceptions are raised with context.

    Args:
        output_temp_path (str): Path to the JSON
        surpress_empty_file_log (bool): 

    Returns:
        tuple[list[dict], int]:
            - A list of dictionaries representing the JSON content
            - An integer representing the number of items in the list.

    Raises:
        Exception: Any exception that is not due to an empty file.
    """
    try:
        with open(path, "r", encoding='utf-8') as f:
            data = json.load(f)
        return data, len(data)

    except json.JSONDecodeError:
        if not surpress_empty_file_log:
            logging.info(f"File is empty: {path}")
        return [], 0
    
    except Exception as e:
        logging.error(f"Error reading {path}: {e}")
        raise Exception(f"Error reading {path}: {e}")
    
def save_to_json(data: list[dict], path: str, mode: str = 'w'):
    """
    Saves a list of dictionaries to a JSON file.

    Args:
        data (list[dict]): The data to save, where each dict represents a row.
        path (str): The file path where the JSON will be written.
        mode (str): File mode.
        header (bool): Whether to write the header row.

    Exceptions:
        Logs an error if saving the file fails.
    """
    try:
        existing_data, _ = load_json(path, True)
        existing_data.extend(data)

        with open(path, mode) as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        logging.info(f"Saved {len(data)} entries to {path}.")

    except Exception as e:
        logging.error(f"Failed to save data to {path}: {e}")
        raise

def remove_file(path: str, on_success_msg: str = None) -> None:
    """
    Attempts to remove the file at the specified path.

    Args:
        path (str): The file path to remove.
        on_success_msg (str, optional): Custom message to log on successful removal.

    Logs:
        - INFO: On successful file removal.
        - WARNING: If the file does not exist.
        - ERROR: If permission is denied or other unexpected errors occur.
    """
    try:
        os.remove(path)
        if on_success_msg:
            logging.info(on_success_msg)
        else:
            logging.info(f"File removed: {path}")

    except FileNotFoundError:
        logging.warning(f"File not found, cannot remove: {path}")

    except PermissionError:
        logging.error(f"Permission denied when trying to remove: {path}")
        
    except Exception as e:
        logging.error(f"Unexpected error removing file {path}: {e}")

def collect_files(source_folder: str, filtered_by_type: bool, file_type: str = "") -> list:
    """
    Search a given source folder for files, as the option for filter it by extensions.

    Args:
        source_folder (str): The path to the folder from which to collect file names.
        filtered_by_type (bool): If True it will check for the extension.
        file_type (str): The file extension to search.

    Returns:
        list: list of filenames in the given directory, optionaly filtered by the given file type
    """
    files = []
    for f in os.listdir(source_folder):
        if filtered_by_type:
            if f.endswith(file_type):
                files.append(f)
            else:
                logging.warning(f"{f} is not a file {file_type}")
        else:
            files.append(f)
    
    if files:
        logging.info(f"Found {len(files)} {file_type} files: {' '.join(files)}")
    else:
        logging.info(f"No {file_type} files found in {source_folder}.")
        
    return files
