import os
import logging
from utils.file_utils import create_json_file, collect_files

def create_directory(path: str) -> None:
    """
    Create a directory on the specified path

    Args:
        path(str): Path to create the directory

    Raises:
        OSError: If there is an error creating the directory
    """

    if os.path.exists(path):
        logging.info(f"Directory already exists: {path}.")
        return
    
    try:
        os.makedirs(path)
        logging.info(f"Directory {path}: created successfully.")

    except OSError as e:
        logging.error(f"Failed to create directory '{path}': {e}")
        raise OSError(f"Failed to create directory '{path}': {e}") from e

def setup_project_directories(config: dict) -> None:
    """
    Use utility modules to create the initial setup of the type dataset/{name}/{name}_temp.json

    Args:
        config (dict): configuration dictionary
    """
    create_directory("logs")

    dir_path = os.path.join("datasets/translation")
    create_directory(dir_path)

    data_folder = os.path.join(dir_path, config["name"])
    create_directory(data_folder)

    if config.get("source_folder"):
        original_source = os.path.join(config["source_folder"])
        file_name = collect_files(original_source, True, config["reader"])

        for file in file_name:
            file_path = os.path.join(data_folder, os.path.splitext(file)[0]) + "_translated.json"
            
            if not os.path.exists(file_path):
                create_json_file(os.path.splitext(file_path)[0] + "_temp.json")
            
    else:
        file_path = os.path.join(data_folder, config["name"] + "_translated.json")

        if not os.path.exists(file_path):
            create_json_file(os.path.splitext(file_path)[0] + "_temp.json")
        