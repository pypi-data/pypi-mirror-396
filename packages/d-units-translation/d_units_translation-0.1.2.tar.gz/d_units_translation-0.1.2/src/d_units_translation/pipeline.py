from utils.directory_utils import setup_project_directories
from utils.logging_utils import configure_logging
from utils.config_utils import load_config
from utils.correction_utils import correct_translation
from dispatchers.load_data_dispatcher import load_data
from controllers.main_controller import main_controller
import os

def translation_dataset(config_location: str) -> None:
    """
    Manages the end-to-end workflow for dataset translation and correction.

    Args:
        config_location: The filesystem path to the project configuration file (JSON)
    """
    config = load_config(config_location)
    setup_project_directories(config)

    log_output = "logs/translation.log"
    configure_logging(log_output)

    data = load_data(config)
    for dataset, file_name in data:
        output_path = os.path.join("datasets/translation", config["name"], file_name + "_translated.json")
        output_correction_path = os.path.join("datasets/translation", config["name"], file_name + "_corrected.json")

        if not os.path.exists(output_path):
            main_controller(dataset, config, output_path)
        
        if not os.path.exists(output_correction_path):
            correct_translation(output_path, output_correction_path, log_output, config)
