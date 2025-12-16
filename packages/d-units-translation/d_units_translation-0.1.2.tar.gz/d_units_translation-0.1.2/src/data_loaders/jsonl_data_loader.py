from datasets import Dataset, DatasetDict
from utils.file_utils import collect_files
from utils.processing_utils import extract_text_from_obj
import logging
import json
import os    

def process_json_entries_to_dataset(config: dict, file: str, filtered: bool = False) -> DatasetDict:
    """
    This function filters and extracts specified columns from each entry in the combined data,
    cleans the text, generates a unique ID for each item, and compiles the results into a Dataset.

    Args:
        config (dict): Configuration dictionary.
        combined_data (list[dict]): List of raw JSON-like dictionaries to process.
        filtered (bool): bool indicating if the DatasetDict will have all columns or only the one it will translate

    Returns:
        Dataset: A HuggingFace Dataset object constructed from the processed entries.
    """
    full_path = os.path.join(config["source_folder"], file)
    elements = []

    with open(full_path, 'r') as f:
        for line in f:
            entry = json.loads(line)
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


def load_jsonl_datasets(config: str) -> list[tuple[DatasetDict, str]]:
    """
    Loads and processes JSONL files from the specified source folder into Hugging Face `DatasetDict`, returning
    each datasetDict with the file base name without the extension. 

    Args:
        config (dict): Configuration dictionary.

    Returns:
        DatasetDict: A Hugging Face DatasetDict object with a single split 
        that combines all the datasets built from the `.tml` files.
    
    Raises:
        ValueError: If any error occurs while reading or processing the files.
    """
    try:
        json_files = collect_files(config["source_folder"], True, ".jsonl")
        data = []

        for file in json_files:
            ds_dict = process_json_entries_to_dataset(config, file)
            data.append((ds_dict, os.path.splitext(file)[0]))

        return data
    
    except Exception as e:
        logging.error(f"Error processing JSONL files: {e}")
        raise ValueError(f"Failed to load JSONL datasets: {e}") from e
    