from datasets import Dataset, DatasetDict
from utils.file_utils import collect_files
from utils.processing_utils import extract_text_from_obj
import logging
import ijson
import os

def build_dataset_from_json(config: dict, file: str, filtered: bool = False) -> DatasetDict:
    """
    Builds a Hugging Face DatasetDict from an json file by extracting and cleaning
    specific elements defined in the configuration.

    Args:
        config (dict): Configuration dictionary
        file (str): Name of the XML file to be processed
        filtered (bool): bool indicating if the DatasetDict will have all columns or only the one it will translate

    Returns:
        DatasetDict: A Hugging Face DatasetDict with a single train split containing 
        one example composed of the extracted elements and a generated hash ID.
    """
    try:
        full_path = os.path.join(config["source_folder"], file)
        elements = []

        with open(full_path, 'r') as files:
            parser = ijson.items(files, 'item')

            for entry in parser:
                filtered_entry = {}
                
                if filtered:
                    for column in config["columns2translate"]:
                        if column in entry and entry[column]:
                            raw_text = entry[column]
                            clean_text = extract_text_from_obj(raw_text)

                            if clean_text.strip():
                                filtered_entry[column] = clean_text
                else:
                    for key, value in entry.items():
                        if value:
                            clean_text = extract_text_from_obj(value)
                            if clean_text.strip():
                                filtered_entry[key] = clean_text

                if filtered_entry:
                    elements.append(filtered_entry)

            dataset = Dataset.from_list(elements)

            dataset_dict = DatasetDict({config["split_name"]: dataset})

            return dataset_dict

    except FileNotFoundError as e:
        logging.error(f"File not found: {file}: {e}")

    except Exception as e:
        logging.error(f"Unexpected error processing file {file}: {e}")

def load_json_datasets(config: dict) -> list[tuple[DatasetDict, str]]:
    """
    Loads and processes JSON files from the specified source folder into Hugging Face `DatasetDict`, returning
    each datasetDict with the file base name without the extension. 

    Args:
        config (dict): Configuration dictionary.

    Returns:
        list[tuple[DatasetDict, str]]: A list of tuples, each containing a Hugging Face DatasetDict 
        and the base name of the corresponding CSV file (without extension).
    
    Raises:
        ValueError: If any error occurs while reading or processing the files.
    """
    try:
        json_files = collect_files(config["source_folder"], True, ".json")
        data = []

        for file in json_files:
            ds_dict = build_dataset_from_json(config, file)
            data.append((ds_dict, os.path.splitext(file)[0]))

        return data
    
    except Exception as e:
        logging.error(f"Error processing JSON files: {e}")
        raise ValueError(f"Failed to load JSON datasets: {e}") from e
