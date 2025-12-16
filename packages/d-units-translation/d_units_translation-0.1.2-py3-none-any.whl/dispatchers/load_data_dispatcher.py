from datasets import DatasetDict
from data_loaders.hugging_face_data_loader import load_hugging_face_dataset
from data_loaders.xml_tml_data_loader import load_xml_tml_datasets
from data_loaders.json_data_loader import load_json_datasets
from data_loaders.csv_data_loader import load_csv_datasets
from data_loaders.jsonl_data_loader import load_jsonl_datasets
import logging

def load_data(config: dict) -> list[tuple[DatasetDict, str]]:
    """
    For the reader in the config, it calls the apropriate function to load the dataset or convert it to one.
    
    Supported readers:
        - hugging_face
        - csv
        - xml
        - json
        - jsonl

    Args:
        config (dict): Configuration dictionary

    Returns:
        dataset (dict): Loaded dataset based in the config

    Raises:
        ValueError: If the reader type specified in the config is not supported.
    """
    match config.get("reader"):
        case "hugging_face":
            return load_hugging_face_dataset(config)

        case "csv":
            return load_csv_datasets(config)

        case ("xml" | "tml"):
            return load_xml_tml_datasets(config)

        case "json":
            return load_json_datasets(config)
        
        case "jsonl":
            return load_jsonl_datasets(config)

        case _:
            logging.error(f"Unknown reader type: {config.get('reader')}")
            raise ValueError(f"Unknown reader type: {config.get('reader')}")
