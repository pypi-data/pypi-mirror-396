import json
import logging

def load_config(path: str) -> list[dict]:
    """
    Load and parse a JSON file that contains either a single configuration dict or
    a list of configuration dicts

    Args:
        path(str): Path to the JSON configuration file.

    Returns:
        list[dict]: Parsed configuration as a dictionary.

    Raises:
        ValueError: If the loaded configuration is empty or not a dictionary.
    """
    try:
        with open(path, 'r') as cfg:
            data = json.load(cfg)
            logging.info(f"{path} file sucessfully loaded")

        return data
    
    except FileNotFoundError as e:
        logging.error(f"Config file not found: {path}")
        raise
    
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in config file: {path} ({e})")
        raise

