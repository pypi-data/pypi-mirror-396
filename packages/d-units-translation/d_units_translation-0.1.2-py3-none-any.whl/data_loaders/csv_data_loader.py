from datasets import DatasetDict, load_dataset
from utils.file_utils import collect_files
import logging
import os

def load_csv_datasets(config: dict, filtered: bool = False) -> list[tuple[DatasetDict, str]]:
    """
    Loads and processes CSV files from the specified source folder into Hugging Face `DatasetDict`, returning
    each datasetDict with the file base name without the extension. 

    Args:
        config (dict): Configuration dictionary.
        filtered (bool): bool indicating if the DatasetDict will have all columns or only the one it will translate
    
    Returns:
        list[tuple[DatasetDict, str]]: A list of tuples, each containing a Hugging Face DatasetDict 
        and the base name of the corresponding CSV file (without extension).
    
    Raises:
        ValueError: If any error occurs while reading or processing the files.
    """
    try:
        data = []
        csv_files = collect_files(config["source_folder"], True, ".csv")

        for file in csv_files:
            file_path = os.path.join(config["source_folder"], file)
            
            dataset_dict = load_dataset("csv", data_files={config["split_name"]: file_path})

            if filtered:
                dataset_dict = dataset_dict.map(
                    lambda x: {k: x[k] for k in config["columns2translate"]},
                    remove_columns=[col for col in dataset_dict[config["split_name"]].column_names if col not in config["columns2translate"]]
                )

            data.append((dataset_dict, os.path.splitext(file)[0]))

        return data
    
    except Exception as e:
        logging.error(f"Error processing TML files: {e}")
        raise ValueError(f"Failed to load TML datasets: {e}") from e
        