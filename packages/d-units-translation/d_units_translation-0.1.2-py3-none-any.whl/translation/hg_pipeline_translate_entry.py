from functools import lru_cache
from transformers import Pipeline, AutoTokenizer, PreTrainedTokenizerBase
import logging
import re


@lru_cache(maxsize=None)
def token_len(text: str, tokenizer: PreTrainedTokenizerBase, entry_id: str) -> int:
    """
    Calculates the number of tokens in a given text using the specified tokenizer.
    This function is memoized for performance optimization when the same text is
    tokenized multiple times.

    Args:
        text (str): The input text whose token count is to be computed.
        tokenizer (PreTrainedTokenizerBase): A Hugging Face tokenizer instance used to encode the text.
        entry_id (str): An identifier for the text entry (used for tracking/logging).

    Returns:
        int: The number of tokens in the text.
    """
    try:
        return len(tokenizer.encode(text, add_special_tokens=False, truncation=False))
    
    except Exception as e:
        logging.warning(f"Tokenization failed for text segment entry {entry_id}: {e}")
        return 0
        
    
def split_sentence_recursive(sub_sentences: list, config: int, tokenizer: PreTrainedTokenizerBase, entry_id: str) -> list:
    """
    Recursively splits long text segments into smaller parts that fit within the
    configured token limit.

    Args:
        sub_sentences (list): A list of text fragments to process.
        config (dict): Configuration dictionary containing 'max_tokens' (int).
        tokenizer (PreTrainedTokenizerBase): A Hugging Face tokenizer instance used to encode the text.
        entry_id (str): An identifier for the text entry (used for tracking/logging).

    Returns:
        list: A list of text fragments, each within the token limit.
    
    Raises:
        RuntimeError: If Exceeded maximum number of recursion.
    """
    result = []

    for sub in sub_sentences:
        try:
            if token_len(sub, tokenizer, entry_id) <= config["max_tokens"]:
                result.append(sub)
            else:
                mid = len(sub) // 2
                split_point = sub.rfind(" ", 0, mid)
                if split_point == -1:
                    split_point = mid

                first_part = sub[:split_point]
                second_part = sub[split_point:]

                if token_len(first_part, tokenizer, entry_id) > config["max_tokens"]:
                    result.extend(split_sentence_recursive([first_part], config, tokenizer, entry_id))
                else:
                    result.append(first_part)

                if token_len(second_part, tokenizer, entry_id) > config["max_tokens"]:
                    result.extend(split_sentence_recursive([second_part], config, tokenizer, entry_id))
                else:
                    result.append(second_part)
        
        except RecursionError as e:
            logging.error(f"Exceeded maximum recursion depth when splitting text on entry {entry_id}: {e}")
            raise RuntimeError(f"Exceeded maximum recursion depth when splitting text: {entry_id}") from e

    return result

def split_sentences(text: str, config: dict, tokenizer: PreTrainedTokenizerBase, entry_id: str) -> list:
    """
    Splits the input text into sentences, and further divides any sentence exceeding the maximum token limit 
    into smaller chunks at commas or semicolons. Them recursively splits longer chunks at half.

    Args:
        text (str): Input text to split.
        config (dict): Configuration dictionary.
        tokenizer (PreTrainedTokenizerBase): A Hugging Face tokenizer instance used to encode the text.
        entry_id (str): An identifier for the text entry (used for tracking/logging).
    
    Return:
        list: A list of sentences or sub-sentences, each within the max token limit.
    
    Raises:
        KeyError: IF missing max_tokens key in the config file.
    """ 

    if "max_tokens" not in config:
        raise KeyError("'max_tokens' missing in config")

    sentences = re.split(r'(?<!\d)(?<=[.!?])(?<!\n\d\.)\s+', text)
    result = []

    for s in sentences:
        s = s.strip()
        num_tokens = len(tokenizer.encode(s, add_special_tokens=False, truncation=False))

        if num_tokens > config["max_tokens"]:
            sub_sentences = re.split(r'(?<=[,;])\s+', s)

            for ss in sub_sentences:
                try:
                    if token_len(ss, tokenizer)  > config["max_tokens"]:
                        result.extend(split_sentence_recursive([ss], config, tokenizer, entry_id))
                    else:
                        result.append(ss)

                except Exception as e:
                    logging.warning(f"Failed to process sub-sentence entry {entry_id}: {e}")
                    return []

        else:
            result.append(s)
            
    return result
    
def translate_text_with_model(pipe: Pipeline, config: dict) -> callable:
    """
    Creates and returns a translation function that uses the provided Hugging Face
    translation pipeline.

    Args:
        pipe (Pipeline): A Hugging Face translation pipeline instance (e.g., from `transformers.pipeline("translation")`).
        config (dict): Configuration dictionary.

    Returns:
        callable: A `translate_text` function with the signature:
            translate_text(config: dict, text: str, entry_id: str) -> str
    
    Raises:
        RuntimeError: If it fails to load the tokenizer.
    """

    try:
        tokenizer = AutoTokenizer.from_pretrained(config["model"], model_max_length=1_000_000)
    except Exception as e:
        raise RuntimeError(f"Failed to load tokenizer for model '{config.get('model', '?')}'") from e

    def translate_text(config: dict, text: str, entry_id: str) -> str:
        """
        Translates the given text using the model pipeline.

        Args:
            config (dict): Configuration dictionary with translation settings.
            text (str): The text to translate.
            entry_id (str): An identifier for the text entry (used for tracking/logging).

        Returns:
            str: The translated text, concatenated from all processed chunks.
        
        Raises:
            RunTimeError: if the splitting function failed.
            Warning: Logs a warning (does not raise) if an individual line fails translation.
        """
        if not text:
            return ""

        try:
            processed_lines = split_sentences(text, config, tokenizer, entry_id)
        except Exception as e:
            raise RuntimeError(f"Sentence splitting failed for entry {entry_id}: {e}")

        result = []

        for line in processed_lines:
            try:
                outputs = pipe(line)
            except Exception as e:
                logging.warning(f"Translation failed for line in entry {entry_id}: {e}")
                return ""

            for o in outputs:
                if isinstance(o, dict) and "translation_text" in o:
                    result.append(o["translation_text"])
                elif isinstance(o, str):
                    result.append(o)

        return "".join(result)

    return translate_text
    
