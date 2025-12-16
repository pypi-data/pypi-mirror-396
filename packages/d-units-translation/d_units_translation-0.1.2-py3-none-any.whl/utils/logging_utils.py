import logging
import re

def configure_logging(log_folder: str, verbose: bool = False):
    """
    Configures logging for the application.

    Args:
        log_folder (str): 
        verbose (bool): If True, sets level to DEBUG. Otherwise, INFO.
    """
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    file_handler = logging.FileHandler(log_folder)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        handlers=[stream_handler, file_handler]
    )

def id_log_error(log_file_path: str) -> set:
    """
    
    """
    failed_ids = set()

    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(r"entry (\S+):", line)
            if match:
                failed_ids.add(match.group(1))
    
    return failed_ids
