from datasets import DatasetDict, load_dataset
import logging

def load_hugging_face_dataset(config: dict, filtered: bool = False) -> list[tuple[DatasetDict, str]]:
    """
    Loads the dataset from hugging face based in the configuration dictionary

    Args:
        config (dict): Configuration dictionary
        filtered (bool): bool indicating if the DatasetDict will have all columns or only the one it will translate
    
    Returns:
        list[tuple[DatasetDict, str]]: A list of tuples, each containing a Hugging Face DatasetDict 
        and the base name of the corresponding CSV file (without extension).
    
    Raises:
        ValueError: If any error occurs while reading or processing the files.
    """
    try:
        dataset = load_dataset(config["dataset"], config.get("version"))
        logging.info(f"{config['dataset']} dataset sucessfully loaded")

        if filtered:
            for split in dataset.keys():
                available_columns = dataset[split].column_names
                keep_columns = [col for col in config["columns2translate"] if col in available_columns]
                dataset[split] = dataset[split].select_columns(keep_columns)

        return [(dataset, config['name'])]
    
    except Exception as e:
        logging.error(f"Dataset couldn't be loaded: {config['dataset']} - {config.get('version')} - {e}")
        raise ValueError(f"Dataset couldn't be loaded: {config['dataset']} - {config.get('version')} - {e}") from e
