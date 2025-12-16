from utils.file_utils import load_json
from utils.backup_utils import backup_if_needed, finalize_output_file
from dispatchers.translate_dispatcher import translate_method
from controllers.translation_controller import translation_controller
import logging
import os



def main_controller(dataset: dict, config: dict, output_path: str) -> None:
    """
    This function processes each entry in the provided dataset according to the configuration.
    It skips entries that were already processed, call the translate methods for new entries, 
    and saves them in batches for recovery in case of interruption.

    Args:
        dataset (dict): A dictionary of dataset.
        config (dict): Configuration dictionary.
        output_path (str): Final path to write the processed data.
    """
    output_temp_path = os.path.join(os.path.splitext(output_path)[0] + "_temp.json")
    _, count_temp = load_json(output_temp_path)

    trans_method = translate_method(config)
    col_id = config.get("col_id")
    idx = 0
    skipped_count = 0
    current_batch_size = 0
    translated_batch = []

    for split in dataset.keys():
        for _, entry in enumerate(dataset[split]):
            if(idx < count_temp):
                skipped_count += 1
                idx += 1
                continue

            else:
                if idx == count_temp:
                    logging.info(f"Skipped {skipped_count}/{count_temp} Entries.")

                try:
                    if col_id not in entry:
                        entry['id'] = idx

                    result = translation_controller(entry, split, trans_method, config)
                    
                except Exception as e:
                    logging.error(f"Error processing entry {entry.get('id', entry.get(col_id))}: {e}")
                    continue
                
                translated_batch.append(result)
                current_batch_size += 1
                logging.info(f"Translated Entry {current_batch_size}/{config['backup_interval']}: {result.get('id', entry.get(col_id))}")

            idx += 1

            translated_batch, current_batch_size = backup_if_needed(translated_batch,
                                                                    current_batch_size,
                                                                    idx,
                                                                    config['backup_interval'],
                                                                    output_temp_path)
    
    finalize_output_file(translated_batch, output_temp_path, output_path)
