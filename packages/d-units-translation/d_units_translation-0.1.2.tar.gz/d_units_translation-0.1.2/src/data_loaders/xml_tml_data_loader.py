import xml.etree.ElementTree as ET
from datasets import Dataset, DatasetDict
from utils.file_utils import collect_files
import logging
import os

def extract_text(element: ET.Element) -> str:
    """
    Recursively extracts and concatenates text content from a XML or TML element and its children.

    Args:
        element: The root element to extract text from.

    Returns:
        A string containing all the text content.
    """
    text_content = []

    def recursive_extract(elem):
        if elem.text:
            text=elem.text.replace("\n"," \n ")
            text_content.append(text)
        for child in elem:
            recursive_extract(child)
            if child.tail:
                text = child.tail.replace("\n", " \n ")
                text_content.append(text)

    recursive_extract(element)
    return ''.join(text_content).strip()


def build_dataset_from_tml(config: dict, file: str, filtered: bool = False) -> DatasetDict:
    """
    Builds a Hugging Face DatasetDict from an XML or TML file by extracting and cleaning
    specific elements defined in the configuration.

    Args:
        config (dict): Configuration dictionary
        file (str): Name of the XML or TML file to be processed
        filtered (bool): bool indicating if the DatasetDict will have all columns or only the one it will translate

    Returns:
        DatasetDict: A Hugging Face DatasetDict with a single train split containing 
        one example composed of the extracted elements and a generated hash ID.
    """
    try:
        tree = ET.parse(os.path.join(config["source_folder"], file))
        root = tree.getroot()

        elements = {}
        if root:
            for child in root:
                if not filtered or child.tag in config["columns2translate"]:
                    clean_text = extract_text(child)
                    elements[child.tag] = clean_text


        dataset = Dataset.from_list([elements])

        dataset_dict = DatasetDict({config["split_name"]: dataset})

        return dataset_dict
    
    except ET.ParseError as e:
        logging.error(f"TML parsing error in file {file}: {e}")

    except FileNotFoundError as e:
        logging.error(f"File not found: {file}: {e}")

    except Exception as e:
        logging.error(f"Unexpected error processing file {file}: {e}")

def load_xml_tml_datasets(config: dict) -> list[tuple[DatasetDict, str]]:
    """
    Loads and processes XML or TML files from the specified source folder into Hugging Face `DatasetDict`, returning
    each datasetDict with the file base name without the extension. 

    Args:
        config (dict): Configuration dictionary.

    Returns:
        DatasetDict: A Hugging Face DatasetDict object with a single split 
        that combines all the datasets built from the files.

    Raises:
        ValueError: If any error occurs while reading or processing the files.
    """
    try:
        tml_files = collect_files(config["source_folder"], True, config.get("reader"))
        data = []

        for file in tml_files:
            ds_dict = build_dataset_from_tml(config, file)
            data.append((ds_dict, os.path.splitext(file)[0]))

        return data
    
    except Exception as e:
        logging.error(f"Error processing XML/TML files: {e}")
        raise ValueError(f"Failed to load XML/TML datasets: {e}") from e
