from utils.file_utils import save_to_json, remove_file
import logging
import shutil

def backup_if_needed(translated_dataset: list, entry_count: int, entries_processed: int, 
                     backup_interval: int, temp_path: str) -> tuple[list, int]:
    """
    Performs a backup of the translated dataset to a temporary JSON file at specified intervals.

    Args:
        translated_dataset (list): List of translated entries to be backed up.
        entry_count (int): Number of entries currently in the translated_dataset.
        entries_processed (int): Total number of entries processed so far.
        backup_interval (int): Number of entries to process before triggering a backup.
        temp_path (str): File path to save the backup JSON.
    
    Returns:
        tuple[list, int]: A tuple containing the updated translated dataset and the updated entry count.
    """
    if entries_processed % backup_interval == 0:
        try:
            save_to_json(translated_dataset, temp_path)
            
        except Exception as e:
            logging.error(f"Failed to backup data at entry {entries_processed}: {e}")
            raise

        return [], 0
    return translated_dataset, entry_count

    
def finalize_output_file(translated_data: list, temp_path: str, final_path: str) -> None:
    """
    Finalizes the output by appending any remaining translated data to a temporary file,
    copying the temporary file to the final destination, and removing the temporary file.

    Args:
        translated_data (list): List of translated entries not yet saved to the temporary file.
        temp_path (str): Path to the temporary backup file.
        final_path (str): Path where the final output file should be saved.
    """
    try:
        if len(translated_data) > 0:
            save_to_json(translated_data, temp_path)

        shutil.copy(temp_path, final_path)
        remove_file(temp_path, f"Backup file removed: {temp_path}")
        logging.info(f"Final output saved to {final_path}")

    except Exception as e:
        logging.error(f"Error finalizing output file: {e}")
        raise
