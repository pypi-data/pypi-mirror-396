import logging

def translation_controller(entry: any, split: str, method: callable, config: dict) -> dict:
    """
    Controls the translation process for a given data entry.

    Args:
        entry (any): The input data entry containing the text fields to translate.
        split (str): A label or tag indicating the dataset split (e.g., 'train', 'test', 'validation').
        method (callable): The translation function to apply.
        config (dict): Configuration dictionary.

    Returns:
        dict: A dictionary containing the original entry plus:
    
    Raises:
        Exception: If an entry's ID cannot be determined or if other critical errors occur 
        while reading or writing files.
    """
    result = entry.copy()
    result["split"] = split

    for col in config["columns2translate"]:
        try:
            value = entry[col]

            try:
                entry_id = entry.get("id")
                if entry_id is None:
                    entry_id = entry[config.get("col_id")]

            except Exception as e:
                logging.error(f"Failed to get entry_id for entry: {e}")
                raise

            result.update({col + "_translated": translate_value(entry_id, value, method, config)})

        except Exception as e:
            logging.warning(f"Error translating column '{col}': {e}")
            result.update({col + "_translated": ""})

    return result


def translate_value(entry_id: str | int , value: any, method, config:dict) -> any:
    """
    Recursively applies a translation method to a value (string, list, or dict).

    Args:
        entry_id (str | int): Identifier for the current entry, passed to the translation method.
        value (any): The value to translate.
        method (callable): The translation function to apply.
        config (dict): Configuration dictionary.
    
    Returns:
        any: The translated value.
    """
    if isinstance(value, list):
        return [translate_value(entry_id, v, method, config) for v in value]

    elif isinstance(value, dict):
        return {k: translate_value(entry_id, v, method, config) for k, v in value.items()}

    elif isinstance(value, str):
        return method(
            config=config,
            text=value,
            entry_id=entry_id)

    else:
        return value
    