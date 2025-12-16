from translation.deepl_translation import translate_text_with_deepl
from translation.hg_pipeline_translate_entry import translate_text_with_model
from transformers import pipeline
import logging

def translate_method(config: dict) -> callable:
    """
    Function that chooses the method of translation.

    Supported methods:
        - deepL
        - models

    Args:
        config (dict): Configuration dictionary.
        
    Returns:
        callable: The translation function corresponding to the selected method.

    Raises:
        ValueError: If the specified method is not supported.
    """
    match config["method"]:
        case "deepL":
            return translate_text_with_deepl
        
        case "model":
            try:
                translator = pipeline("translation", model=config["model"])
                return translate_text_with_model(translator, config)
            except Exception as e:
                logging.error(f"Failed to initialize or use translation model '{config.get('model', 'unknown')}': {e}")
                raise Exception(f"Failed to initialize or use translation model '{config.get('model', 'unknown')}': {e}") from e

        case _:
            logging.error(f"Unknown method: {config['method']}")
            raise ValueError(f"Unknown method: {config['method']}")
        