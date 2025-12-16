from utils.file_utils import load_json
from translation.deepl_translation import translate_text_DeepTranslator
from utils.file_utils import load_json
from utils.logging_utils import id_log_error
from utils.file_utils import create_json_file
from utils.backup_utils import backup_if_needed, finalize_output_file
import logging
import ijson
import time
import os

def safe_translate(source_lang: str, target_lang: str, text: str, item_id: str, retries: int = 5, delay: int = 5):
    """
    Try to translate text using translate_text_DeepTranslator with retries.
    
    Args:
        source_lang (str): source language
        target_lang (str): target language
        text (str): text to translate
        item_id (str): identifier for logging/debug
        retries (int): number of retries before failing
        delay (int): seconds to wait before retrying

    Returns:
        str: translated text, or empty string if all retries fail
    """
    for attempt in range(1, retries + 1):
        try:
            return translate_text_DeepTranslator(source_lang, target_lang, text, item_id)
        
        except Exception as e:
            logging.info(f"[{item_id}] Translation attempt {attempt} failed: {e}")

            if attempt < retries:
                time.sleep(delay)

            else:
                logging.error(f"[{item_id}] Giving up after {retries} attempts.")
                return ""

def correct_translation(path: str, output_path: str, log_output: str, config: dict) -> None:
    """
    Corrects previously failed translations in a JSON file based on a log of failed IDs,
    re-translates missing text fields, and safely writes updated data to an output file
    with periodic backups

    Args:
        path (str): Path to the input JSON file containing the original translated data.
        output_path (str): Path to the output JSON file.
        log_output (str): Path to the log file containing.
        config (dict): configuration dictionary.

    Raises:
        Exception: If an entry's ID cannot be determined or if other critical errors occur 
        while reading or writing files.
    """
    output_temp_path = os.path.join(os.path.splitext(output_path)[0] + "_temp.json")

    if not os.path.exists(output_temp_path):
        create_json_file(output_temp_path)
        
    current_batch_size = 0

    _, count_temp = load_json(output_temp_path)
    corrected_batch = []

    failed_ids = id_log_error(log_output)

    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(ijson.items(f, "item")):
            if idx < count_temp:
                continue
            
            
            try:
                line_id = line.get("id")
                if line_id is None:
                    line_id = line[config.get("col_id")]

            except Exception as e:
                logging.error(f"Failed to get entry_id for entry: {e}")
                raise
        
            if str(line_id) in failed_ids:
                for column in config["columns2translate"]:
                    if line[f"{column}_translated"] == "":
                        line[f"{column}_translated"] = safe_translate(config["source_language"], 
                                                                      config["target_language"], 
                                                                      line[f"{column}"], 
                                                                      line.get("id", "unknown"))

            corrected_batch.append(line)


            corrected_batch, current_batch_size = backup_if_needed(corrected_batch,
                                                                   current_batch_size,
                                                                   idx + 1,
                                                                   config['backup_interval'],
                                                                   output_temp_path)
            
        finalize_output_file(corrected_batch, output_temp_path, output_path)
